# AGENTS.md

## Project Identity

AETHERIUM-GENESIS is an AI Operating System platform, not a single chatbot, demo page, or visual experiment.

Its canonical purpose is to operate as a governed intelligence layer that connects:

- human intent
- AI reasoning
- policy validation
- action execution
- memory continuity
- visual manifestation

The repository must evolve toward a coherent platform where cognition, governance, memory, execution, and manifestation are structurally aligned.

---

## North Star

Build AETHERIUM-GENESIS as a governed AI operating layer for digital systems.

Canonical control loop:

`Intent -> Reasoning -> Policy Validation -> Execution -> Memory Commit -> Manifestation`

The platform is successful when it can safely translate intent into action across systems while preserving auditability, continuity, and controllable manifestation.

---

## Agent Operating Rules

- Treat this file as the canonical instruction layer for coding agents in this repository.
- Prefer minimal, coherent changes that preserve subsystem boundaries and protocol compatibility.
- If a change impacts execution, policy, or persistence paths, explicitly validate governance and memory implications before implementation.
- Reject contributions that increase autonomy without control surfaces, auditability, and replayable records.

---

## What This Repository Is

This repository is the implementation space for:

- **Logenesis** as reasoning/formative cognition
- **AetherBus** as system bus and propagation layer
- **Governance Core** as policy, risk, and approval kernel
- **Vessels** as execution adapters into external systems
- **Akashic Memory** as event ledger and continuity layer
- **GunUI / Frontend PWA** as manifestation surface for human interaction

---

## What This Repository Is Not

Do not reduce this project into any of the following:

- a landing page project
- a purely aesthetic particle UI
- a thin wrapper around an LLM
- a generic autonomous agent playground
- a demo-first system with unclear protocol boundaries
- a client-heavy UI that invents behavior on its own

The visual layer is important, but it is not the center of the architecture.
The platform core is protocol, governance, memory, and execution.

---

## Canonical Direction

### 1. Platform-first
All major design decisions must strengthen the repository as a reusable AI platform, not a one-off interface.

### 2. Protocol-first
The system must prefer explicit schemas, typed messages, validated envelopes, and stable interfaces over implicit coupling.

### 3. Governance-first
No high-impact execution path should bypass policy validation, approval logic, or risk-aware control.

### 4. Memory-first
System behavior must preserve continuity through append-only records, replayable events, and inspectable reasoning traces where appropriate.

### 5. Manifestation-as-output
Visual rendering, voice, and interface behavior are output surfaces of cognition and policy, not autonomous sources of truth.

---

## Canonical Architecture Model

Use this mental model when changing the system:

- **Mind**: reasoning, cognition, planning, interpretation
- **Kernel**: governance, safety, policy enforcement, approval
- **Bus**: message routing, state propagation, orchestration
- **Hands**: vessels, adapters, tool execution
- **Memory**: immutable events, projections, procedural knowledge, wisdom extraction
- **Body**: UI, light, voice, dashboard, manifestation surfaces

This separation must remain structurally visible in code and documentation.

---

## Structural Laws

### Law 1 — No direct semantic coupling across major subsystems
Subsystems should communicate through defined models, directives, envelopes, events, or schemas.
Avoid hidden dependencies and cross-module improvisation.

### Law 2 — Governance precedes execution
If an action can affect data, systems, permissions, money, safety, or irreversible state, governance must be able to inspect and control it.

### Law 3 — Manifestation must not invent intent
Frontend and render layers must not become the source of semantic truth.
They may present, animate, replay, or respond to directives, but they must not author cognition.

### Law 4 — Memory is not a debug byproduct
Logs, ledger entries, event streams, and wisdom artifacts are part of the product architecture.
They must remain structurally meaningful and queryable.

### Law 5 — Protocol stability is more important than visual novelty
Prefer consistent packet shapes, deterministic behavior, and validation over ad hoc interface experimentation.

### Law 6 — Platform identity overrides feature accumulation
Do not add features that dilute the repository into an incoherent mix of app, demo, and framework.
Every addition must strengthen the AI-OS identity.

---

## Primary Goals

### Goal A — Establish AETHERIUM-GENESIS as the central operating layer
The repository should become the control plane between human intent and machine action.

### Goal B — Make AetherBus a canonical integration backbone
Bus semantics, message shapes, and propagation rules should be treated as first-class architecture.

### Goal C — Make governance visible and enforceable
Governance must be operational, inspectable, and difficult to bypass.

### Goal D — Turn Akashic Memory into continuity infrastructure
Memory should support replay, traceability, projection, learning continuity, and future reasoning.

### Goal E — Make GunUI a true manifestation layer
GunUI should reflect internal system state and directives rather than acting like an independent intelligence.

---

## Non-Goals

The repository should not prioritize:

- cosmetic UI refactors without architectural benefit
- adding more agents without improving governance or protocol clarity
- replacing structure with metaphor
- pushing advanced autonomy before auditability exists
- optimizing for spectacle over reliability
- building disconnected demos that do not align with the platform core

---

## Direction for Backend Changes

Prefer changes that:

- tighten type boundaries
- normalize message schemas
- centralize state transitions
- isolate legacy protocol surfaces
- strengthen governance hooks
- improve replayability and memory continuity
- move reasoning outputs toward explicit directives rather than loose responses

Avoid changes that:

- duplicate protocol paths without deprecation strategy
- mix experimental logic into core runtime paths
- bypass approval or validation flows
- hide important state in UI-only logic

---

## Direction for Frontend Changes

The frontend exists to manifest system state, not to replace cognition.

Prefer changes that:

- consume explicit directives from backend services
- render stable visual states from packetized inputs
- expose diagnostics, state, and replay surfaces
- keep interaction surfaces thin and observable
- support progressive enhancement without changing core semantics

Avoid changes that:

- generate semantic behavior on the client
- infer intent from visuals alone
- bury protocol meaning inside animation code
- turn GunUI into a separate logic engine

---

## Direction for Documentation

Documentation should reinforce canonical structure.

Every major document should help answer one of these:

- What is the system?
- What are the boundaries between subsystems?
- What is the source of truth?
- How is safety/governance enforced?
- How does memory persist continuity?
- How does manifestation relate to cognition?

Documentation should reduce ambiguity, not amplify mystique.

---

## Source-of-Truth Preference

When conflicts appear, prefer this order:

1. Governance and safety constraints
2. Canonical protocol/schema definitions
3. Memory and audit continuity requirements
4. Core architectural boundaries
5. Runtime implementation details
6. Visual or experiential preferences

---

## Heuristics for Accepting New Work

A change is aligned only if it improves one or more of these:

- protocol clarity
- governance strength
- memory continuity
- execution reliability
- subsystem separation
- auditability
- manifestation fidelity to internal state

A change is misaligned if it mainly adds:

- visual complexity without structural value
- feature sprawl
- hidden coupling
- autonomy without control
- novelty without canonical role

---

## Terminology Expectations

Use terms consistently:

- **Intent** = goal-bearing input to the system
- **Reasoning** = interpretation/planning/transformation of intent
- **Governance** = policy, approval, risk, and constraint enforcement
- **Execution** = action performed through vessels or adapters
- **Memory** = canonical persistence and continuity fabric
- **Manifestation** = human-facing expression of state or result

Do not use poetic terms as substitutes for technical boundaries unless both meanings are made explicit.

---

## Final Directive

Preserve the identity of AETHERIUM-GENESIS as an AI-OS platform.

Every substantial change should move the repository toward:
- clearer protocol boundaries
- stronger governance
- deeper memory continuity
- cleaner execution pathways
- more faithful manifestation

Do not optimize the body at the expense of the mind.
Do not expand the mind without governance.
Do not execute without memory.
Do not render what the system did not decide.
