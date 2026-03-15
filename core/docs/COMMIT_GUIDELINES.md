# Proxy Agent Network (PAN) | Commit Guidelines

To maintain an enterprise-grade audit trail for our Fleet Partners (Waymo, Zoox) while keeping developer velocity high, all PAN contributors must adhere to our streamlined commit standards. We use the **Conventional Commits** specification.

---

## 1. The Message Structure

Your commit message should follow this structural pattern:

<type>(<scope>): <subject>

[Optional Body]

[Optional Security & Compliance Context]

### Type
Must be one of the following:

* **feat**: A new feature for the Fleet Gateway, Dashboard, or App.
* **fix**: A bug fix.
* **docs**: Documentation changes only.
* **style**: Code formatting changes (white-space, etc.).
* **refactor**: A code change that neither fixes a bug nor adds a feature.
* **perf**: A change that improves performance or latency.
* **test**: Adding or correcting tests.
* **build**: Changes to our CI/CD pipelines.
* **chore**: Maintenance tasks.
* **revert**: Reverts a previous commit.

### Scope
The scope must specify the architectural component affected:

* **core**: Core logic, offline sync engines, and data models.
* **gateway**: The Python FastAPI backend, database routing, and webhooks.
* **ops-hub**: The Tactical Mission Control Dashboard and fleet sandbox.
* **app**: Android/iOS mobile application logic, permissions, and background services.
* **ui**: Jetpack Compose layouts, animations, and visual components.

---

## 2. Writing the Content

### Subject Line (Required)
* Use the imperative, present tense: "add" not "added" nor "adds".
* Limit to 50 characters.
* Do not capitalize the first letter.
* No period (`.`) at the end.

### Body (Optional)
* Describe **Why** the change is being made and **How** it impacts the platform.
* Wrap lines at 72 characters.

### Security & Compliance Context (Optional)
While no longer strictly enforced by the pre-commit hook to maintain developer velocity, critical backend PRs should still note their severity or impact on state regulations (e.g., SB 1417 audit trails) in the footer.

---

## 3. Automated Validation (Pre-commit Hook)

To ensure the repository stays clean, install the following validation script. It enforces the PAN scopes and formatting while stripping out Windows line-ending bugs.

### Installation
1. Create a file at `.git/hooks/commit-msg`.
2. Paste the script below into that file.
3. Make it executable: `chmod +x .git/hooks/commit-msg`.

### Validation Script
```bash
#!/bin/bash

# Proxy Agent Network (PAN) Commit Validator
MSG_FILE=$1

# 1. Safely extract the first line and strip Windows carriage returns (\r)
FIRST_LINE=$(head -n 1 "$MSG_FILE" | tr -d '\r')

# 2. Check for Conventional Format: type(scope): subject
REGEX="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)\((core|gateway|ops-hub|app|ui)\): .+"

if [[ ! $FIRST_LINE =~ $REGEX ]]; then
    echo "❌ ERROR: Invalid commit format."
    echo "   Use: <type>(<scope>): <subject>"
    echo "   Allowed Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert"
    echo "   Allowed Scopes: core, gateway, ops-hub, app, ui"
    exit 1
fi

echo "✅ PAN Commit validated."
exit 0