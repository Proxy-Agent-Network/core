# Proxy Agent Network (PAN) | Commit Guidelines

To maintain an enterprise-grade audit trail for our Fleet Partners (Waymo, Zoox) and state regulators (Arizona DPS), all PAN contributors must adhere to strict commit standards. We use the **Conventional Commits** specification, supplemented with mission-critical physical and compliance metadata.

---

## 1. The Message Structure

Your commit message should follow this structural pattern:

<type>(<scope>): <subject>

[Optional Body]

[Security & Protocol Context]
Severity: <SEV-LEVEL>
Protocol Version: <VERSION>
Hardware Impact: <DESCRIPTION>
Compliance Impact: <DESCRIPTION>

[Breaking Changes]
[Ref]

### Type
Must be one of the following:

* **feat**: A new feature for the Fleet Gateway or Agent SDK.
* **fix**: A bug fix.
* **docs**: Documentation changes only (e.g., SLA, ORP manuals).
* **style**: Code formatting changes (white-space, etc.).
* **refactor**: A code change that neither fixes a bug nor adds a feature.
* **perf**: A change that improves API routing or UWB homing latency.
* **test**: Adding or correcting tests (especially for M2H webhook ingestion).
* **build**: Changes to our CI/CD pipelines.
* **chore**: Maintenance tasks.
* **revert**: Reverts a previous commit.

### Scope
The scope must specify the architectural component affected:

* **core**: L402 settlement, Lightning Network logic, and M2H state machines.
* **gateway**: The Fleet API, UDS fault ingestion, and webhook routing.
* **compliance**: SB 1417 Audit Engine and cryptographic hashing of Optical Health Reports.
* **hardware**: TPM 2.0 / Secure Enclave attestation, GPS/UWB geofencing.
* **ops-hub**: The Tactical Mission Control Dashboard and telemetry UI.

---

## 2. Security & Compliance Context (Mandatory)

Because the PAN codebase triggers real-world physical actions on $150k+ autonomous vehicles, you must include the following metadata in your commit body or footer:

* **Severity**: `SEV-1` (Physical asset risk/Enclave spoofing), `SEV-2` (SLA/API outage), `SEV-3` (Minor UI bugs), or `NONE`.
* **Protocol Version**: Target version (e.g., `v2026.1`).
* **Hardware Impact**: Specify if the change affects Vanguard Agent hardware key generation or UWB beaconing.
* **Compliance Impact**: Specify if the change modifies the SB 1417 audit log schema or ORP (Optical Reclamation Protocol) liability limits.

---

## 3. Writing the Content

### Subject Line
* Use the imperative, present tense: "change" not "changed" nor "changes".
* Limit to 50 characters.
* Do not capitalize the first letter.
* No period (`.`) at the end.

### Body
* Describe **Why** the change is being made and **How** it impacts AV fleet operations.
* Wrap lines at 72 characters.

### Breaking Changes
All breaking changes must be documented in the footer starting with `BREAKING CHANGE:` followed by a description of the change and the migration path for integrated Fleet API endpoints.

---

## 4. Automated Validation (Pre-commit Hook)

To prevent invalid commits from reaching the Mesa Pilot repository, install the following validation script. It enforces the new AV infrastructure scopes and mandatory compliance metadata.

### Installation
1. Create a file at `.git/hooks/commit-msg`.
2. Paste the script below into that file.
3. Make it executable: `chmod +x .git/hooks/commit-msg`.

### Validation Script
#!/bin/bash

# Proxy Agent Network (PAN) Commit Validator
MSG_FILE=$1
COMMIT_MSG=$(cat "$MSG_FILE")

# 1. Regex for Conventional Commits: type(scope): subject
REGEX="^(feat|fix|docs|style|refactor|perf|test|build|chore|revert)\((core|gateway|compliance|hardware|ops-hub)\): .+"

if [[ ! $COMMIT_MSG =~ $REGEX ]]; then
    echo "❌ ERROR: Invalid commit message format."
    echo "Expected: <type>(<scope>): <subject>"
    echo "Types: feat, fix, docs, style, refactor, perf, test, build, chore, revert"
    echo "Scopes: core, gateway, compliance, hardware, ops-hub"
    exit 1
fi

# 2. Check for Mandatory Metadata
METADATA_FIELDS=("Severity:" "Protocol Version:" "Hardware Impact:" "Compliance Impact:")
MISSING_FIELDS=()

for field in "${METADATA_FIELDS[@]}"; do
    if ! echo "$COMMIT_MSG" | grep -q "$field"; then
        MISSING_FIELDS+=("$field")
    fi
done

if [ ${#MISSING_FIELDS[@]} -ne 0 ]; then
    echo "❌ ERROR: Missing mandatory Security & Compliance Context."
    for missing in "${MISSING_FIELDS[@]}"; do
        echo "   - Missing field: $missing"
    done
    exit 1
fi

echo "✅ PAN Commit message validated."
exit 0