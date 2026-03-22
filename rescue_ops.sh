#!/bin/bash
echo "🚨 Initiating SEV-1 Rescue Operation..."

# 1. Time-travel to Phase 2 to rescue our deleted folders
git checkout 80b3fa5 -- backend pan_gateway proxy-core hardware-node

# 2. Ensure our modern architecture folders exist
mkdir -p apps/backend/src
mkdir -p apps/backend/gateway
mkdir -p hardware/proxy-core
mkdir -p hardware/python-node

# 3. Safely copy the contents (using -a to grab everything, avoiding wildcards entirely)
cp -a backend/. apps/backend/src/
cp -a pan_gateway/. apps/backend/gateway/
cp -a proxy-core/. hardware/proxy-core/
cp -a hardware-node/. hardware/python-node/

# 4. Remove the old root directories
rm -rf backend pan_gateway proxy-core hardware-node

echo "✅ Rescue complete! Files safely transplanted."