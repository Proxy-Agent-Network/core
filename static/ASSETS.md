# Proxy Agent Network: Static Assets & Multimedia Guide

This directory contains the visual and auditory assets that power the **Mission Control v1.0** gamified experience.

## 🎨 Visual Assets (`/images`)

### Magic Marvin (`magic_marvin_dance.webp`)
* **Type:** Animated WebP (Transparent)
* **Usage:** Summoned via `summonMarvin()` in the dashboard upon Level Up or high-tier task completion.
* **Styling:** The dashboard applies a dynamic `drop-shadow` filter based on the active `--accent` CSS variable of the current theme.

## 🔊 Audio Assets (`/audio`)
The system uses a tiered audio feedback loop to provide variable reinforcement based on task value (Sats).

### Tiered Task Completion (Sats-based)
| File | Trigger Condition |
| :--- | :--- |
| `Coin_Tier1.mp3` | Basic Task Completion (> 0 Sats) |
| `Coin_Tier2.mp3` | Mid-Tier Task Completion (≥ 50,000 Sats) |
| `Coin_Tier3.mp3` | High-Tier / Jackpot Task (≥ 100,000 Sats) |

### Milestone SFX
* **`Leveled_Up_Strings.mp3`**: Triggered when a Node's XP crosses a 5,000 XP threshold, increasing the `level` integer.
* **`Bonus_Streak_Harp.mp3`**: Triggered when a node completes a task on a consecutive day, incrementing the `streak_days` in `registry.db`.
* **`marvin_laughing.mp3`**: **Easter Egg.** Triggered by double-clicking the Magic Marvin sprite while he is active on screen.

## 🔡 Fonts (Google Fonts Integration)
While fonts are served via the Google Fonts API in `dashboard.html`, the following styles are mapped to specific themes:
* **Radical Retro:** `'Press Start 2P'` (8-bit style)
* **Groovy Greens:** `'Shrikhand'` (60s flower power)
* **Cyberpunk:** `'Orbitron'` (Futuristic/Neon)
* **Paperback Noir:** `'Special Elite'` (Typewriter)

## 🛠️ Contribution Guidelines
1. **Audio:** Keep `.mp3` files under 200KB for rapid playback without latency.
2. **Images:** Use `.webp` for animations to maintain transparency and low file size.
3. **Themes:** When adding new assets, ensure they align with the CSS variables defined in the `:root` of `dashboard.html`.