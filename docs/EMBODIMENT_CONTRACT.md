# EMBODIMENT CONTRACT (v1.0)

## 1. Philosophy
This document defines the **Application Binary Interface (ABI) of Cognition**.
It acts as the "Nervous System" connecting the "Brain" (LLM/Model) to the "Body" (GunUI/Light).
It ensures that visual manifestation is not random art, but an **observable truth** of the system's internal state.

## 2. The Contract Schema (JSON)

Every cognitive cycle MUST produce or update this structure before manifestation occurs.

```json
{
  "contract_version": "1.0",
  "timestamp": "ISO-8601-UTC",

  // 2.1 TEMPORAL STATE (The 'When')
  // Defines the phase of existence in the current timeline.
  "temporal_state": {
    "phase": "THINKING",       // ENUM: IDLE, LISTENING, THINKING, MANIFESTING, ERROR
    "stability": 0.8,          // 0.0 (Volatile/Changing) -> 1.0 (Stable/Locked)
    "duration_ms": 120         // Time spent in this current phase
  },

  // 2.2 COGNITIVE METADATA (The 'How')
  // Meta-parameters describing the mental effort, NOT the content.
  "cognitive": {
    "effort": 0.75,            // 0.0 (Reflex) -> 1.0 (Deep Reasoning)
    "uncertainty": 0.1,        // 0.0 (Sure) -> 1.0 (Lost/Guessing)
    "latency_factor": 0.3      // External network/processing lag normalized
  },

  // 2.3 INTENT (The 'What')
  // The nature of the will being exercised.
  "intent": {
    "category": "ANALYTIC",    // ENUM: CHIT_CHAT, ANALYTIC, CREATIVE, SYSTEM_OPS
    "purity": 0.95             // How clear is the intent? (0.0 = Mixed/Confused)
  }
}
```

## 3. The Mapping Logic (The Translator)
The EmbodimentAdapter must strictly follow these laws when converting the Contract into Visual Parameters.

**Law 1: Conservation of Energy (Inertia)**
 * High cognitive.effort = Slower, heavier particle movement (High Mass).
 * Low cognitive.effort = Fast, erratic, light movement (Low Mass).

**Law 2: Visibility of Entropy (Turbulence)**
 * High cognitive.uncertainty = Increased turbulence and chromatic_aberration.
 * Low cognitive.uncertainty = High structural_integrity (Sharp edges).

**Law 3: Topology of Intent (Shape)**
 * ANALYTIC = Geometric (Hexagon, Cube, Grid).
 * CREATIVE = Organic (Fluid, Nebula, Swarm).
 * SYSTEM_OPS = Linear (Data streams, Terminal lines).
 * IDLE/LISTENING = Sphere (The resting potential).

## 4. Operational Boundaries
 * **No Smoothing:** The raw state must be truthful. Smoothing happens at the renderer (client), not the contract.
 * **Silence is Valid:** If temporal_state.phase is IDLE, visual output minimizes to "Pilot Light" mode.
