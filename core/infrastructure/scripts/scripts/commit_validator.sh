#!/bin/bash

# PROXY PROTOCOL - COMMIT MESSAGE VALIDATOR v1.0
# Used for both local Git hooks and CI/CD pipeline enforcement.
# ----------------------------------------------------

MSG_FILE=$1

# Ensure a file path was provided
if [ -z "$MSG_FILE" ]; then
    echo "❌ ERROR: No commit message file path provided."
    echo "Usage: $0 <path_to_msg_file>"
    exit 1
fi

COMMIT_MSG=$(cat "$MSG_FILE")

# 1. Regex for Conventional Commits: type(scope): subject
# Matches: feat(core): add something
# Scopes: core, sdk-node, gov, hardware, ui
REGEX="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)\((core|sdk-node|gov|hardware|ui)\): .+"

if [[ ! $COMMIT_MSG =~ $REGEX ]]; then
    echo "❌ ERROR: Invalid commit message format."
    echo "Expected: <type>(<scope>): <subject>"
    echo "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert"
    echo "Scopes: core, sdk-node, gov, hardware, ui"
    exit 1
fi

# 2. Check for Mandatory Metadata (Security & Protocol Context)
METADATA_FIELDS=("Severity:" "Protocol Version:" "Hardware Impact:" "Legal Impact:")
MISSING_FIELDS=()

for field in "${METADATA_FIELDS[@]}"; do
    if ! echo "$COMMIT_MSG" | grep -q "$field"; then
        MISSING_FIELDS+=("$field")
    fi
done

if [ ${#MISSING_FIELDS[@]} -ne 0 ]; then
    echo "❌ ERROR: Missing mandatory Security & Protocol Context."
    for missing in "${MISSING_FIELDS[@]}"; do
        echo "   - Missing field: $missing"
    done
    exit 1
fi

echo "✅ Commit message validated."
exit 0
