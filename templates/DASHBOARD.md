# Proxy Agent Mission Control: Dashboard Architecture

This directory contains the Jinja2/HTML templates and logic for the Proxy Agent Network's primary monitoring interface.

## 🎨 The Theme Engine
The dashboard utilizes a robust CSS-in-HTML strategy where the `<body>` tag's `data-theme` attribute dictates the UI's aesthetic. A pre-render script injection prevents FOUC (Flash of Unstyled Content) by loading the saved theme from `localStorage` before the DOM paints.

### Core Themes
| Theme ID | Description | Primary Font |
| :--- | :--- | :--- |
| `business` | **(Default)** Clean, corporate, light mode. | Inter |
| `retro` | 8-bit arcade aesthetic with pixel fonts. | Press Start 2P |
| `paperback` | Old typewriter style on paper texture. | Special Elite |
| `cyberpunk` | High-tech, low-life neon pink/yellow. | Orbitron |
| `deepsea` | High-contrast teal and dark blue. | Montserrat |
| `vampire` | Gothic red and gold with blackletter type. | UnifrakturMaguntia |
| `groovy` | 1960s psychedelic floral palette. | Shrikhand |

### Dynamic CSS Variables
Themes now control logic-based colors for the XP Ledger to ensure readability on both light and dark backgrounds:
* `--bg`: Page background.
* `--accent`: Primary highlight color (Marvin glow, Progress Bar).
* `--bonus-color`: Color for "Rubber-Band" entries (Gold/Brown).
* `--secret-color`: Color for "System Bypass" entries (Neon Green/Forest Green).
* `--ledger-font`: Dynamic sizing to accommodate wide pixel fonts.

## 🎛️ Audio Rack
The header includes a persisted Audio Control Rack:
* **Volume Slider:** Controls global volume (0.0 to 1.0).
* **Mute Toggle:** Instantly mutes/unmutes all SFX.
* **Persistence:** Volume settings are saved to `localStorage` and restored on page load.

## 📜 Session XP Ledger
The dashboard features a detailed transaction modal (`#xp-modal`) that tracks gains in real-time.

### Hierarchy & Nesting
The ledger uses visual indentation to group rewards with their parent task:
1.  **Base Task:** The primary trigger (e.g., `TASK-A1B2`).
2.  **Nested Rewards:** Indented items like `└─ 📈 Rubber-Band Boost` or `└─ ⚡ Secret Bypass Reward`.

### Logic & Race Conditions
* **Polling:** The client polls `/debug/node_status` every **1000ms** to ensure rapid-fire tasks are captured distinctly.
* **ID Capture:** On detecting an XP gain, the client immediately fetches `/debug/view_tasks` to associate the specific Task ID with the gain, preventing duplicate or generic entries.

## 📈 Gamification & Logic
The client-side logic separates "Server Truth" from "Display Truth" to handle bonuses and persistence.

1.  **Persistence Strategy:** `sessionBonusXP` is stored in `localStorage`. This prevents "rubber-banding" (visual XP drops) when the server hasn't yet processed a client-side bonus.
2.  **Reset Detection:** The client tracks `lastServerXP`. If the server reports a value *lower* than the last known value, the client assumes a System Reset occurred and wipes all local history and bonuses.
3.  **Rubber-Band Boost:** Nodes under **Level 5** receive a visual 100% XP match on every task to accelerate early progression.

## 🪄 Magic Marvin & Easter Eggs
The `summonMarvin()` function controls the lifecycle of the wizard sprite.

* **Summoning:** Occurs on `Level Up` and significant XP gains.
* **Interaction:** **Double-Clicking** Marvin triggers a spin animation and a laughing sound effect.
* **Konami Code:** Entering `↑ ↑ ↓ ↓ ← → ← → B A` triggers:
    * **System Bypass:** A glitch overlay effect.
    * **Secret Reward:** A staged +30 XP bonus applied to the next completed task.
