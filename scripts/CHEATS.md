# Proxy Agent Network: Developer Cheats & Scripts

This guide contains quick snippets and "cheat codes" for testing the gamification engine and Mission Control dashboard without needing a real agent network.

## 🧪 Quick Database Reset
If you need to wipe the `registry.db` and start fresh (Level 1, 0 XP):

**Endpoint:** `GET /debug/reset_me`
**Browser URL:** `http://localhost:5000/debug/reset_me`

> **Warning:** This deletes all nodes, tasks, and history. It re-initializes the default "NODE-001".

---

## ⚡ Manual Task Injection (CURL)
Use these commands in your terminal (Git Bash or PowerShell) to simulate task completions and test the audio/visual feedback.

### 1. Basic Task (Coin Tier 1)
Grants 500 XP + 500 Sats. Good for testing the progress bar.
\```bash
curl -X POST http://localhost:5000/api/v1/tasks/complete \
-H "Content-Type: application/json" \
-d '{"task_id": "TEST-001", "node_id": "NODE-001"}'
\```

### 2. High-Value Task (Coin Tier 3)
Grants 500 XP + 150,000 Sats. Triggers the "Jackpot" sound.
```bash
curl -X POST http://localhost:5000/api/v1/tasks/complete \
-H "Content-Type: application/json" \
-d '{"task_id": "JACKPOT-999", "node_id": "NODE-001", "payout": 150000}'
```

---

## 🚀 The "Level Grinder" Loop
Want to see "Magic Marvin" dance without clicking 10 times? Run this loop in your terminal to fire 10 tasks in rapid succession.

**Bash (Git Bash / Mac / Linux):**
```bash
for i in {1..10}; do 
  curl -X POST http://localhost:5000/api/v1/tasks/complete \
  -H "Content-Type: application/json" \
  -d "{\"task_id\": \"AUTO-$i\", \"node_id\": \"NODE-001\"}"; 
  sleep 1; 
done
```

**PowerShell:**
```powershell
1..10 | ForEach-Object {
    Invoke-RestMethod -Uri "http://localhost:5000/api/v1/tasks/complete" -Method Post -ContentType "application/json" -Body '{"task_id": "AUTO-PS", "node_id": "NODE-001"}'
    Start-Sleep -Seconds 1
}
```

---

## 🕵️ Easter Eggs
* **Double-Click Marvin:** If Marvin is visible, double-clicking him triggers `marvin_laughing.mp3`.
* **Konami Code:** (Planned for v1.1) - currently does nothing.
