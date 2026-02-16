# Proxy Agent Mission Control: Dashboard & Admin Architecture

This directory contains the Jinja2/HTML templates and logic for the Proxy Agent Network's primary monitoring and administrative interfaces.

## 🎨 The Theme Engine (v1.3 - Decoupled)
The network utilizes a shared `theme-engine.js` that manages UI aesthetics across all pages using the `<html>` tag's `data-theme` attribute. 

### Core Themes
| Theme ID | Description | Primary Font |
| :--- | :--- | :--- |
| `business` | **(Default)** Clean, corporate, light mode. | Inter |
| `retro` | 8-bit arcade aesthetic with pixel fonts. | Press Start 2P |
| `paperback` | Vintage typewriter style on tan paper texture. | Special Elite |
| `cyberpunk` | High-tech dark mode with neon pink/yellow accents. | Orbitron |
| `deepsea` | High-contrast teal and dark blue (Dark Mode). | Montserrat |
| `vampire` | Gothic red and gold with blackletter type. | UnifrakturMaguntia |
| `groovy` | **Hippie VW MiniBus:** Retro Teal, Purple, and Marigold. | Shrikhand |

### UI Stability & Persistence
* **FOUC Prevention:** A pre-render script injection in the `<head>` prevents "Flash of Unstyled Content" by loading the saved theme from `localStorage` before the DOM paints.
* **Layout Stability:** The `.theme-picker-ui` uses a `min-width: 180px` and a "Loading..." placeholder to prevent Cumulative Layout Shift (CLS) in the header on refresh.
* **Dynamic CSS Variables:** Themes control logic-based colors for the XP Ledger and XP Bar (e.g., `--xp-glow: transparent` for Paperback/Groovy) to ensure maximum readability.

## 🎛️ Admin Control Center (`admin.html`)
The operational nerve center for the Core Team to manage network behavior manually.

1. **Task Injection:** Allows manual deployment of tasks with custom rewards to test node response.
2. **Danger Zone:** Provides a global system reset to wipe node XP and task history via `/debug/reset_me`.
3. **Node Registry Search:** A real-time client-side filter that allows operators to find specific Node IDs, Levels, or XP values instantly using an `input` listener on the table body.

## 📜 Session XP Ledger & Audio
The dashboard features a detailed transaction modal (`#xp-modal`) that tracks gains in real-time.

### Hierarchy & Nesting
The ledger uses visual indentation to group rewards with their parent task:
1.  **Base Task:** The primary trigger (e.g., `TASK-18A84175`).
2.  **Nested Rewards:** Indented items like `└─ 📈 Rubber-Band Boost` or `└─ ⚡ Secret Bypass Reward`.

### Persistent Audio Rack
The header includes an Audio Control Rack with volume and mute persistence. SFX are tiered based on reward size:
* **Tier 1-3 Coins:** Triggered based on XP gain magnitude.
* **Level Up Strings:** Triggered when the total XP crosses a 5000 XP threshold.

## 📈 Gamification & Logic
The client-side logic separates "Server Truth" from "Display Truth" to handle rewards.

1. **Race Conditions:** The client polls `/debug/node_status` every **1000ms**. On gain detection, it immediately fetches `/debug/view_tasks` to associate the specific Task ID.
2. **Reset Detection:** If `currentServerXP < lastServerXP`, the client triggers a local purge of `sessionBonusXP` and history.
3. **Rubber-Band Boost:** Nodes under **Level 5** receive a visual 100% XP match on every task to accelerate early progression.

## 🪄 Magic Marvin & Easter Eggs
The `summonMarvin()` function controls the lifecycle of the wizard sprite.

* **Interaction:** **Double-clicking** Marvin triggers a spin animation and a laughing sound effect. (Marvin is hidden in Business/Paperback themes).
* **Konami Code:** Entering `↑ ↑ ↓ ↓ ← → ← → B A` triggers a "System Bypass" glitch overlay and a staged +30 XP bonus applied to the next completed task.