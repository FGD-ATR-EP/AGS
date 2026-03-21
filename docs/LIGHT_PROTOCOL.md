# LIGHT PROTOCOL SPECIFICATION (v0.1)

## 1. Purpose
The **Light Protocol** is the standardized interface for **Observable Cognitive State Signaling**.
It is not a visualization layer, a decoration, or a media output. It is a strict protocol that translates internal cognitive processes (reasoning, retrieval, hesitation, decision) into observable luminous states.

In this architecture, Light is the **API of the Cognitive Infrastructure**.

## 2. Definition
*   **Protocol Name:** LightProtocol
*   **Role:** Universal Interface for Cognitive Execution
*   **Transmission Medium:** Luminous Parameters (Color, Turbulence, Density, Motion)
*   **Observer:** Human Operator (via Retina/Screen)

## 3. Signal Types
The protocol defines specific signals for cognitive metabolic states. These are **not** emotional expressions.

### 3.1 Load (Cognitive Effort)
*   **Definition:** The intensity of processing power currently engaged.
*   **Visual Signal:** Particle Density & Turbulence.
*   **Low Load:** Sparse, slow-moving particles (Idle).
*   **High Load:** Dense, high-velocity vortex (Reasoning/Generating).

### 3.2 Confidence (certainty)
*   **Definition:** The probability of correctness or alignment with the Ground Truth.
*   **Visual Signal:** Structural Stability & Sharpness.
*   **High Confidence:** Geometric shapes (Cube, Sphere) with defined edges.
*   **Low Confidence:** Amorphous forms (Cloud, Fog, Scatter).

### 3.3 Uncertainty (Entropy)
*   **Definition:** The level of ambiguity in the input or the reasoning path.
*   **Visual Signal:** Color Shift & Flicker.
*   **Stable:** Constant Hue.
*   **Uncertain:** Rapid hue shifts, chromatic aberration artifacts.

### 3.4 Execution Phase (Lifecycle)
*   **Perception:** Inward flow (gathering data).
*   **Interpretation:** Rapid oscillation (weighing vectors).
*   **Manifestation:** Outward expansion (delivering result).
*   **Recall:** Deep/Dark intensity (accessing storage).

## 4. Implementation Mapping
This abstract protocol is implemented in the codebase via `VisualParameters`.

| LightProtocol Concept | Implementation Field (`VisualParameters`) |
| :--- | :--- |
| **Cognitive State** | `base_shape` |
| **Processing Load** | `particle_density` |
| **Internal Conflict** | `turbulence` |
| **Intent/Context** | `color_palette` |

## 5. Non-Goals
To ensure engineering integrity, the Light Protocol explicitly rejects the following:

*   **NOT Emotion Simulation:** The system does not "feel" sadness. A blue, slow state indicates "Low Energy/High Inertia," not depression.
*   **NOT UI Decoration:** Light is not a background. It is the primary trace of execution.
*   **NOT Media:** It is not a video player. It is a real-time state renderer.
