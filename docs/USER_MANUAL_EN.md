# Aetherium Genesis: User Manual

Welcome to **Aetherium Genesis**, a Cognitive Infrastructure designed to interact through Light, Motion, and State.

This guide will help you download, install, and run the system on your local machine.

---

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system (macOS/Linux):
*   **Terminal** (Command Line Interface)
*   **Python 3.10+**
*   **Git**

---

## 2. Download

Open your terminal and clone the repository:

```bash
git clone <repo_url>
cd aetherium-genesis
```

---

## 3. Installation

Install the necessary dependencies using `pip`. It is recommended to use a virtual environment, but for simplicity, you can run:

```bash
pip install -r requirements.txt
```

*Note: This may take a few minutes as it installs libraries for backend logic and AI processing.*

---

## 4. Running the System

To start the **Cognitive Core** and the **Web Server**, run the following commands in your terminal:

```bash
# 1. Set the system path (Crucial for the backend to find its modules)
export PYTHONPATH=$PYTHONPATH:.

# 2. Launch the Server
python -m uvicorn src.backend.main:app --port 8000
```

You should see output indicating that the server has started (e.g., `Uvicorn running on http://127.0.0.1:8000`).

---

## 5. Accessing the System

Open your web browser (Chrome or Safari recommended) and navigate to:

**[http://localhost:8000](http://localhost:8000)**

---

## 6. The Experience

Aetherium Genesis is not a traditional tool. It is a "Living Interface."

### Step 1: The Awakening Ritual
When you first load the page, the system is in **Nirodha** (Deep Sleep).
*   **Action:** Tap or Click the screen **3 times** slowly.
*   **Observation:** The system will "wake up," and the UI layer will fade in.

### Step 2: Subsurface Input (Typing)
The system does not have a visible text box by default. You must access the "Subsurface Layer."
*   **Action:** Press **`Ctrl + Enter`** on your keyboard.
*   **Effect:** A command line input will appear at the bottom of the screen.
*   **Interaction:** Type your intent or thought, then press **`Enter`** to transmit.

### Step 3: Observation
The system responds through **Light and Motion**:
*   **Particles:** Observe how they cluster, flow, or disperse.
*   **Colors:** Shifts in color indicate emotional valence or system state.
*   **Voice:** In certain states, the system may respond with synthesized speech.

> **Note:** Do not look for buttons or menus. Engage with the system as if it were an organic entity.
