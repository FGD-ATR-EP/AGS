import time
import uuid
import numpy as np
from typing import Dict, List, Deque, Optional
from collections import deque
from .light_schemas import (
    LightIntent, LightInstruction, LightAction, LightEntity, LightState, PriorityLevel
)
from .formation_manager import FormationManager

class LightControlLogic:
    """
    Light Control Logic (LCL)
    Translates abstract LightIntent into concrete LightInstruction for the renderer.
    Must be deterministic.
    """

    def __init__(self):
        # Gatekeeper State
        self.last_intent_time: Dict[str, float] = {}
        self.intent_timestamps: Dict[str, Deque[float]] = {} # Sliding window for rate limit
        self.RATE_LIMIT = 5.0 # intents per second per source
        self.WINDOW_SIZE = 1.0 # seconds

        # Physics State (NumPy)
        # Initial capacity
        self._capacity = 10000
        self._count = 0

        # Arrays
        self._ids = np.empty(self._capacity, dtype=object)
        self._pos = np.zeros((self._capacity, 2), dtype=np.float32)
        self._vel = np.zeros((self._capacity, 2), dtype=np.float32)
        self._target_pos = np.zeros((self._capacity, 2), dtype=np.float32)
        self._has_target = np.zeros(self._capacity, dtype=bool)
        self._target_colors = np.empty(self._capacity, dtype=object) # Can be None
        self._energy_levels = np.ones(self._capacity, dtype=np.float32)

        # History: Circular buffer? Or just list of tuples for compatibility?
        # Implementing efficient history in numpy is tricky if it needs to match List[Tuple].
        # For performance, we'll keep a separate python list if needed, OR ignore history for physics.
        # But LightEntity expects history.
        # Let's optimize: Only keep history if requested? No, the code appends every tick.
        # We will use a numpy ring buffer for history: (N, 10, 2)
        self._history = np.zeros((self._capacity, 10, 2), dtype=np.float32)
        self._history_idx = 0 # Ring buffer index for all? No, they shift.
        # Shift approach: array[:, :-1] = array[:, 1:]; array[:, -1] = new_pos

        self._id_map: Dict[str, int] = {}

        self.system_energy: float = 100.0
        self.MAX_ENERGY = 100.0

        # Metrics
        self.metrics = {
            "latency": deque(maxlen=100),
            "intent_count": 0
        }

    @property
    def entities(self) -> Dict[str, LightEntity]:
        """
        Reconstructs dictionary view of entities from NumPy state.
        This is expensive and should only be used for snapshots/serialization.
        """
        result = {}
        active_ids = self._ids[:self._count]
        active_pos = self._pos[:self._count]
        active_vel = self._vel[:self._count]
        active_energy = self._energy_levels[:self._count]
        active_history = self._history[:self._count]
        active_target_pos = self._target_pos[:self._count]
        active_has_target = self._has_target[:self._count]
        active_target_colors = self._target_colors[:self._count]

        for i, eid in enumerate(active_ids):
            # Convert history numpy array to list of tuples
            hist = [tuple(h) for h in active_history[i] if not (h[0] == 0 and h[1] == 0)]
            # Note: 0,0 check is naive, but history is init with 0s.
            # Ideally we'd track length. For now, just dumping the whole buffer or non-zero.
            # Actually, let's just return the last 10 points.
            hist = [tuple(p) for p in active_history[i]]

            entity = LightEntity(
                id=str(eid),
                position=tuple(active_pos[i]),
                velocity=tuple(active_vel[i]),
                energy=float(active_energy[i]),
                history=hist
            )
            if active_has_target[i]:
                entity.target_position = tuple(active_target_pos[i])
            if active_target_colors[i] is not None:
                entity.target_color = active_target_colors[i]

            result[str(eid)] = entity
        return result

    @entities.setter
    def entities(self, value: Dict[str, LightEntity]):
        """
        Allows manually setting entities (e.g. for testing).
        """
        self._clear_entities()
        for eid, ent in value.items():
            self._add_entity(eid, ent.position, ent.velocity, ent.energy, ent.target_position, ent.target_color)

    def _ensure_capacity(self, needed: int):
        if self._count + needed > self._capacity:
            new_cap = max(self._capacity * 2, self._count + needed)
            self._resize(new_cap)

    def _resize(self, new_cap: int):
        # Resize all arrays
        self._ids = np.resize(self._ids, new_cap)
        self._pos = np.resize(self._pos, (new_cap, 2))
        self._vel = np.resize(self._vel, (new_cap, 2))
        self._target_pos = np.resize(self._target_pos, (new_cap, 2))
        self._has_target = np.resize(self._has_target, new_cap)
        self._target_colors = np.resize(self._target_colors, new_cap)
        self._energy_levels = np.resize(self._energy_levels, new_cap)
        self._history = np.resize(self._history, (new_cap, 10, 2))
        self._capacity = new_cap

    def _add_entity(self, eid: str, pos, vel, energy, target_pos=None, target_color=None):
        if eid in self._id_map:
            return # Already exists

        self._ensure_capacity(1)
        idx = self._count

        self._ids[idx] = eid
        self._pos[idx] = pos
        self._vel[idx] = vel
        self._energy_levels[idx] = energy

        if target_pos is not None:
            self._target_pos[idx] = target_pos
            self._has_target[idx] = True
        else:
            self._has_target[idx] = False

        self._target_colors[idx] = target_color
        # Init history with current pos
        self._history[idx] = np.zeros((10, 2)) # Clear
        self._history[idx, -1] = pos # Set last to current

        self._id_map[eid] = idx
        self._count += 1

    def _remove_entity_by_index(self, idx: int):
        last_idx = self._count - 1
        eid_to_remove = self._ids[idx]

        if idx != last_idx:
            # Swap with last
            last_eid = self._ids[last_idx]

            self._ids[idx] = self._ids[last_idx]
            self._pos[idx] = self._pos[last_idx]
            self._vel[idx] = self._vel[last_idx]
            self._target_pos[idx] = self._target_pos[last_idx]
            self._has_target[idx] = self._has_target[last_idx]
            self._target_colors[idx] = self._target_colors[last_idx]
            self._energy_levels[idx] = self._energy_levels[last_idx]
            self._history[idx] = self._history[last_idx]

            self._id_map[last_eid] = idx

        # Clear last (optional, helps GC)
        self._ids[last_idx] = None
        self._target_colors[last_idx] = None

        del self._id_map[eid_to_remove]
        self._count -= 1

    def _clear_entities(self):
        self._count = 0
        self._id_map.clear()
        # Arrays remain allocated but logically empty

    def _check_rate_limit(self, source: str) -> bool:
        if source not in self.intent_timestamps:
            self.intent_timestamps[source] = deque()

        now = time.time()
        timestamps = self.intent_timestamps[source]

        while timestamps and timestamps[0] < now - self.WINDOW_SIZE:
            timestamps.popleft()

        if len(timestamps) >= self.RATE_LIMIT:
            return False

        timestamps.append(now)
        return True

    def _check_priority(self, intent: LightIntent) -> bool:
        if intent.priority < PriorityLevel.AMBIENT:
             return False
        return True

    def _check_harmony(self, intent: LightIntent) -> LightIntent:
        if intent.vector:
            vx, vy = intent.vector
            magnitude = (vx**2 + vy**2)**0.5
            MAX_VELOCITY = 1.0
            if magnitude > MAX_VELOCITY:
                scale = MAX_VELOCITY / magnitude
                intent.vector = (vx * scale, vy * scale)

        if intent.intensity is not None and intent.intensity > 1.0:
            intent.intensity = 1.0

        return intent

    def _deduct_energy(self, action: LightAction) -> bool:
        cost = 0.0
        if action == LightAction.MOVE: cost = 0.5
        elif action == LightAction.SPAWN: cost = 2.0
        elif action == LightAction.ERASE: cost = 0.2
        elif action == LightAction.EMPHASIZE: cost = 0.1
        elif action == LightAction.MANIFEST: cost = 5.0
        elif action == LightAction.ANSWER: cost = 0.5

        if self.system_energy >= cost:
            self.system_energy -= cost
            return True
        return False

    def process(self, intent: LightIntent) -> Optional[LightInstruction]:
        start_time = time.time()
        instruction = self._process_internal(intent)

        latency = (time.time() - start_time) * 1000
        self.metrics["latency"].append(latency)
        self.metrics["intent_count"] += 1

        return instruction

    def _process_internal(self, intent: LightIntent) -> Optional[LightInstruction]:
        if not self._check_rate_limit(intent.source):
            return None

        if not self._check_priority(intent):
            return None

        intent = self._check_harmony(intent)

        if not self._deduct_energy(intent.action):
            if intent.action == LightAction.SPAWN:
                return None
            return None

        self.last_intent_time[intent.source] = time.time()

        instruction = None

        if intent.action == LightAction.SPAWN:
            entity_id = str(uuid.uuid4())
            region = intent.region or (0.4, 0.4, 0.6, 0.6)
            x = (region[0] + region[2]) / 2
            y = (region[1] + region[3]) / 2

            self._add_entity(
                eid=entity_id,
                pos=(x, y),
                vel=(0.0, 0.0),
                energy=1.0
            )

            instruction = LightInstruction(
                intent=LightAction.SPAWN,
                target=entity_id,
                region=intent.region,
                color_profile=intent.color_hint or "natural_green",
                shape="organic"
            )

        elif intent.action == LightAction.MOVE:
            vec = intent.vector or (0.0, 0.0)
            strength = intent.intensity if intent.intensity is not None else 1.0

            indices = []
            if intent.target and intent.target in self._id_map:
                indices = [self._id_map[intent.target]]
            elif not intent.target or intent.target == "GLOBAL":
                indices = range(self._count) # All

            if indices:
                # Use slicing if indices is range
                if isinstance(indices, range):
                    count = indices.stop
                    # Break locks
                    self._has_target[:count] = False

                    vx = self._vel[:count, 0]
                    vy = self._vel[:count, 1]

                    impulse_scale = 0.05
                    self._vel[:count, 0] = vx + vec[0] * strength * impulse_scale
                    self._vel[:count, 1] = vy + vec[1] * strength * impulse_scale
                else:
                    # Specific list
                    for idx in indices:
                        self._has_target[idx] = False
                        vx, vy = self._vel[idx]
                        impulse_scale = 0.05
                        self._vel[idx] = (
                            vx + vec[0] * strength * impulse_scale,
                            vy + vec[1] * strength * impulse_scale
                        )

            instruction = LightInstruction(
                intent=LightAction.MOVE,
                target=intent.target,
                vector=vec,
                strength=strength
            )

        elif intent.action == LightAction.ERASE:
            if intent.region:
                r = intent.region
                # Vectorized check
                px = self._pos[:self._count, 0]
                py = self._pos[:self._count, 1]

                mask = (px >= r[0]) & (px <= r[2]) & (py >= r[1]) & (py <= r[3])

                # Deletion while iterating is tricky.
                # It's better to gather IDs to remove, or sort indices descending and remove.
                # Vectorized removal:
                # Actually, filtering might be easier: create new arrays?
                # But swapping is O(1) per remove.
                # If removing many, rebuilding might be faster.
                # Let's iterate backwards.
                indices_to_remove = np.where(mask)[0]
                # Sort descending to remove without affecting other indices (except via swap)
                # Swap removal changes indices, so simple iteration doesn't work if indices change.
                # Wait, if we swap with last, the last one moves.
                # We should use ids to be safe or be very careful.
                # Simplest for now: loop and use _remove_entity_by_index carefully?
                # No, standard swap-remove loop is:
                i = 0
                while i < self._count:
                    px, py = self._pos[i]
                    if r[0] <= px <= r[2] and r[1] <= py <= r[3]:
                        self._remove_entity_by_index(i)
                        # Don't increment i, as new element is at i
                    else:
                        i += 1
            else:
                self._clear_entities()

            instruction = LightInstruction(intent=LightAction.ERASE, region=intent.region)

        elif intent.action == LightAction.EMPHASIZE:
             instruction = LightInstruction(
                intent=LightAction.EMPHASIZE,
                target=intent.target,
                strength=intent.intensity or 1.0,
                color_profile=intent.color_hint or "bright",
                text_content=intent.text_content
            )

        elif intent.action == LightAction.ANSWER:
             instruction = LightInstruction(
                intent=LightAction.ANSWER,
                text_content=intent.text_content
             )

        elif intent.action == LightAction.MANIFEST:
            if not intent.formation_data and intent.shape_name:
                count = self._count if self._count > 0 else 50
                count = max(count, 30)
                intent.formation_data = FormationManager.get_formation(intent.shape_name, count)

            if intent.formation_data:
                target_count = len(intent.formation_data)

                # Spawn if needed
                if self._count < target_count:
                    needed = target_count - self._count
                    self._ensure_capacity(needed)
                    # Bulk spawn?
                    # For now, loop spawn is fine
                    for _ in range(needed):
                        eid = str(uuid.uuid4())
                        self._add_entity(eid, (0.5, 0.5), (0.0, 0.0), 1.0)

                # Assign targets
                # Vectorized assignment?
                # We iterate through formation data and assign to existing indices 0..N

                # Prepare arrays for bulk update
                # Only update up to min(count, target_count)
                limit = min(self._count, target_count)

                # Extract formation data
                formation_arr = np.array(intent.formation_data, dtype=object) # (N, 3)
                # Separate coords and colors
                # formation_data is [(x, y, color), ...]

                # This unpacking might be slow if list is huge, but usually < 10k
                coords = np.array([f[:2] for f in intent.formation_data[:limit]])
                colors = [f[2] for f in intent.formation_data[:limit]]

                self._target_pos[:limit] = coords
                self._has_target[:limit] = True
                self._target_colors[:limit] = colors

            instruction = LightInstruction(
                intent=LightAction.MANIFEST,
                text_content=intent.text_content,
                formation_data=intent.formation_data
            )

        return instruction

    def tick(self, dt: float) -> LightState:
        count = self._count
        if count == 0:
            return LightState(entities={}, system_energy=self.system_energy)

        # Slice active arrays
        pos = self._pos[:count]
        vel = self._vel[:count]
        has_target = self._has_target[:count]
        target_pos = self._target_pos[:count]

        # 1. Formation Physics (Target Seeking) where has_target is True
        # Vectorized conditional logic

        # Calculate forces for all, mask later? Or calculate only for masked?
        # Calculating for all is often faster due to contiguous memory, if mask is dense.
        # But if sparse, indexing is better. Let's assume mixed.

        # Indices with targets
        target_indices = has_target

        if np.any(target_indices):
            # Proportional Control (Spring force)
            k_p = 5.0
            k_d = 0.5

            tx = target_pos[target_indices, 0]
            ty = target_pos[target_indices, 1]
            x = pos[target_indices, 0]
            y = pos[target_indices, 1]
            vx = vel[target_indices, 0]
            vy = vel[target_indices, 1]

            dx = tx - x
            dy = ty - y

            fx = k_p * dx - k_d * vx
            fy = k_p * dy - k_d * vy

            vel[target_indices, 0] += fx * dt
            vel[target_indices, 1] += fy * dt

        # 2. Regular drift/friction where NO target
        no_target_indices = ~target_indices
        if np.any(no_target_indices):
            vel[no_target_indices] *= 0.95

        # 3. Integration
        pos += vel * dt

        # 4. Bounce/Clamp
        # x < 0
        mask_l = pos[:, 0] < 0
        pos[mask_l, 0] = 0
        vel[mask_l, 0] *= -0.8

        # x > 1
        mask_r = pos[:, 0] > 1
        pos[mask_r, 0] = 1
        vel[mask_r, 0] *= -0.8

        # y < 0
        mask_t = pos[:, 1] < 0
        pos[mask_t, 1] = 0
        vel[mask_t, 1] *= -0.8

        # y > 1
        mask_b = pos[:, 1] > 1
        pos[mask_b, 1] = 1
        vel[mask_b, 1] *= -0.8

        # 5. History Update
        # Shift history: (N, 10, 2)
        # old: [0, 1, 2, 3] -> new: [1, 2, 3, new]
        hist = self._history[:count]
        hist[:, :-1, :] = hist[:, 1:, :]
        hist[:, -1, :] = pos

        # Energy Regeneration
        last_activity = max(self.last_intent_time.values()) if self.last_intent_time else 0
        if time.time() - last_activity > 1.0:
            self.system_energy = min(self.MAX_ENERGY, self.system_energy + 5.0 * dt)

        # Return State
        # Performance Note: We return an empty entities dict to avoid
        # massive serialization overhead during the physics loop.
        # Consumers should access the .entities property explicitly if they need a snapshot.
        return LightState(
            entities={},
            system_energy=self.system_energy
        )

    def get_metrics(self) -> Dict:
        avg_latency = sum(self.metrics["latency"]) / len(self.metrics["latency"]) if self.metrics["latency"] else 0.0
        return {
            "avg_latency_ms": avg_latency,
            "total_intents": self.metrics["intent_count"],
            "system_energy": self.system_energy,
            "entity_count": self._count
        }
