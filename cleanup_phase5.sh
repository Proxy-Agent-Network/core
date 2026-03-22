#!/bin/bash
# PAN Monorepo Cleanup Script - Phase 5 (Data, Fixtures, and Tools)

echo "Starting Phase 5: Final Root Directory Polish..."

# 1. Create target directories
mkdir -p apps/backend/data
mkdir -p tests/fixtures
mkdir -p apps/backend/src/tools

# 2. Move Application State (Trying git mv first, falling back to standard mv for untracked files)
echo "Relocating state databases and JSON configs..."
git mv core_memories.json apps/backend/data/ 2>/dev/null || mv core_memories.json apps/backend/data/ 2>/dev/null
git mv agency_lore.db apps/backend/data/ 2>/dev/null || mv agency_lore.db apps/backend/data/ 2>/dev/null
git mv agent_memory.db apps/backend/data/ 2>/dev/null || mv agent_memory.db apps/backend/data/ 2>/dev/null

# 3. Move Test Fixtures
echo "Relocating media test fixtures..."
git mv sample.mp3 tests/fixtures/ 2>/dev/null || mv sample.mp3 tests/fixtures/ 2>/dev/null
git mv sample.mp4 tests/fixtures/ 2>/dev/null || mv sample.mp4 tests/fixtures/ 2>/dev/null

# 4. Move Tooling (We know this one is tracked!)
echo "Relocating AV simulation tools..."
git mv simulate_av_ping.py apps/backend/src/tools/ 2>/dev/null

echo "Phase 5 Cleanup Complete! Please run 'git status' to review."