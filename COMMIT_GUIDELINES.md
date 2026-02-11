# Proxy Protocol Commit Guidelines

To maintain a high-integrity audit trail for our hardware-attested network, all contributors must follow these commit standards. We use the **Conventional Commits** specification supplemented with protocol-specific metadata.

---

## 1. The Message Structure

Your commit message should follow this structural pattern:

```text
<type>(<scope>): <subject>

[Optional Body]

[Security & Protocol Context]
[Breaking Changes]
[Ref]
```

### Type
Must be one of the following:

* **feat**: A new feature for the protocol or SDK.
* **fix**: A bug fix.
* **docs**: Documentation changes only.
* **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc).
* **refactor**: A code change that neither fixes a bug nor adds a feature.
* **perf**: A code change that improves performance.
* **test**: Adding missing tests or correcting existing tests.
* **build**: Changes that affect the build system or external dependencies.
* **ci**: Changes to our CI configuration files and scripts.
* **chore**: Other changes that don't modify src or test files.
* **revert**: Reverts a previous commit.

### Scope
The scope should specify the part of the codebase affected:

* **core**: Protocol logic, settlement, and state machines.
* **sdk-node**: The Node.js/TypeScript SDK.
* **gov**: Jury Tribunal, VRF, and bond logic.
* **hardware**: TPM drivers, GPIO logic, and node daemon.
* **ui**: Dashboard and Jury Portal interfaces.

---

## 2. Security & Protocol Context (Mandatory)

Because our code interacts with physical hardware and legal instruments, you must include the following metadata in your commit body or footer:

* **Severity**: `SEV-1` (Fund loss/PII leak), `SEV-2` (Outage/Desync), `SEV-3` (Minor), or `NONE`.
* **Protocol Version**: Target version (e.g., `v1.6.x`).
* **Hardware Impact**: Specify if the change affects TPM key generation or GPIO interrupts.
* **Legal Impact**: Specify if the change modifies a Power of Attorney (PoA) template.

---

## 3. Writing the Content

### Subject Line
* Use the imperative, present tense: "change" not "changed" nor "changes".
* Don't capitalize the first letter.
* No dot (`.`) at the end.

### Body
* Describe **Why** the change is being made and **What** it does.
* Wrap lines at 72 characters.
* Use the imperative mood: "Add feature" instead of "Added feature".

### Breaking Changes
All breaking changes must be documented in the footer starting with `BREAKING CHANGE:` followed by a description of the change and the migration path.

---

## 4. Setup Instructions

To ensure you always see the template when committing locally, run the following command in your terminal:

```bash
git config commit.template .gitmessage
```

---

> *“Trust is hard-won and mathematically preserved. Your commit history is part of that proof.”*
