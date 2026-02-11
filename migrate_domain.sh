#!/bin/bash

# Configuration
OLD_DOMAIN="proxyagent.network"
NEW_DOMAIN="proxyagent.network"

echo "🚀 Starting domain migration from $OLD_DOMAIN to $NEW_DOMAIN..."

# Use 'find' to get all files, excluding the .git directory to prevent history corruption
# 'sed -i' performs the in-place replacement
find . -type f -not -path '*/\.git/*' -print0 | xargs -0 sed -i "s/$OLD_DOMAIN/$NEW_DOMAIN/g"

echo "✅ Migration complete. Please review changes before committing."