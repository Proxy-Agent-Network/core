# Proxy Agent Mission Control: Dashboard Architecture

This directory contains the Jinja2/HTML templates for the Proxy Agent Network's primary monitoring interface.

## 🎨 The Theme Engine
The dashboard utilizes a CSS-in-HTML strategy where the `<body>` tag's `data-theme` attribute dictates the UI's aesthetic. 

### Core Themes
| Theme ID | Description | Primary Font |
| :--- | :--- | :--- |
| `dark` | Default high-contrast green/black. | Courier New |
| `retro` | 8-bit aesthetic with neon accents. | Press Start 2P |
| `cyberpunk` | High-tech, low-life neon pink/yellow. | Orbitron |
| `groovy` | 1960s psychedelic floral palette. | Shrikhand |
| `vampire` | Gothic red and gold. | UnifrakturMaguntia |

### Adding New Themes
To add a new theme, define a new `[data-theme="id"]` block in the `<style>` section and override the following variables:
* `--bg`: Page background color.
* `--accent`: Primary color for progress bars, borders, and Marvin's glow.
* `--font`: The primary font-family.

## 📈 Gamification Logic
The dashboard communicates with the `/debug/node_status` API every 3 seconds to update the following:

1. **XP Pillbox (`.xp-pill`):** A dynamic element that expands when a task is completed to show "XP Gained" and then collapses back to show "Current XP/Next Level."
2. **Progress Bars:** Visual representation of the `n.xp % 5000` logic.
3. **Sound Triggers:** JavaScript logic checks the previous state against the new state to trigger tiered audio (`Coin_Tier1-3`) based on Satoshi earnings.

## 🪄 Magic Marvin Integration
The `summonMarvin()` function controls the lifecycle of the wizard sprite.
* **Summoning:** Occurs on `window.onload`, `Level Up`, and `Tier 3` task completions.
* **Animation:** Uses CSS transitions to float Marvin from `bottom: -400px` to `bottom: 110px`.
* **Interaction:** A click listener handles the easter egg sound triggers.
