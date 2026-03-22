#!/bin/bash
# PAN Monorepo Cleanup Script - Phase 6 (Static Asset Purge)

echo "Starting Phase 6: Purging Legacy Pre-Pivot Static Assets..."

# 1. Create the archive directory
mkdir -p archive/legacy_web/pre_av_static

# 2. Archive the meme audio files
echo "Archiving legacy audio..."
git mv apps/web/public_website/static/audio archive/legacy_web/pre_av_static/ 2>/dev/null

# 3. Archive the gamified JS engines (Theme, Disco, Synthwave, Matrix)
echo "Archiving legacy theme engines..."
git mv apps/web/public_website/static/js archive/legacy_web/pre_av_static/ 2>/dev/null

# 4. Archive the old CSS (we will use fresh styles for the new site)
echo "Archiving legacy CSS..."
git mv apps/web/public_website/static/css archive/legacy_web/pre_av_static/ 2>/dev/null

# 5. Archive specific meme images while leaving the professional roster alone
echo "Isolating and archiving Marvin..."
git mv apps/web/public_website/static/images/magic_marvin_dance.webp archive/legacy_web/pre_av_static/ 2>/dev/null
git mv apps/web/public_website/static/images/synthwave_bkgd.gif archive/legacy_web/pre_av_static/ 2>/dev/null

# 6. Create clean directories for our Vanguard deployment
mkdir -p apps/web/public_website/static/css
mkdir -p apps/web/public_website/static/js
mkdir -p apps/web/public_website/static/images

echo "Phase 6 Cleanup Complete! Please run 'git status' to review."