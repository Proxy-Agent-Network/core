# Contributing to Legal Engineering

Welcome to the **Proxy Protocol Legal Engineering** track. While much of this repository focuses on hardware and cryptography, our mission—bridging digital intent to physical reality—is impossible without a robust, global legal framework.

We need "Legal Engineers" to help us draft and standardize **Limited Power of Attorney (PoA)** and **Delegation Instruments** that allow AI Agents to operate across every major jurisdiction.

---

## 1. Our Legal Philosophy
The Proxy Protocol treats legal authority as an **"importable library."** When an Agent needs to perform a task in a specific country, it should be able to pull a verified, locally-compliant template that a Human Node can execute.

**We prioritize:**
* **Narrow Scope:** Authority should be the minimum required for the task.
* **Cryptographic Linking:** Every legal act must reference a specific transaction hash.
* **Clarity:** Templates must be understandable by both human judges and AI parsers.

---

## 2. Where to Contribute
All legal templates are located in the `templates/legal/` directory. Each jurisdiction should have its own Markdown file (e.g., `france_poa.md`).

---

## 3. Template Structure
To maintain consistency for our AI parsing engine, all templates must follow this three-part structure:

| Section | Focus | Placeholders |
| :--- | :--- | :--- |
| **A. The Preamble** | Identification of Principal & Node | `[PRINCIPAL NAME]`, `[PROXY NODE ID]` |
| **B. Grant of Authority** | Definition of task scope | `[AGENT_PUBLIC_KEY]`, `[SCOPE]` |
| **C. Indemnity & Term** | Liability & Termination triggers | `[DATE]`, `[ESCROW_TIMER]` |

---

## 4. Technical Requirements
You do not need to be a coder to contribute, but your documents must follow these rules:

* **Markdown Format:** Use standard Markdown (`.md`).
* **Placeholders:** Use square brackets for variable data (e.g., `[DATE]`, `[TX_HASH]`).
* **Citations:** Every template must cite governing legislation at the top (e.g., *UK Powers of Attorney Act 1971*).
* **No Legalese:** We prefer "Plain English" to ensure AI agents can correctly interpret their own authorities.

---

## 5. The Submission Process
1. **Fork the Repo:** Create your own copy of the repository.
2. **Draft your Template:** Create a new file in `templates/legal/`.
3. **Submit a Pull Request (PR):**
   * Title your PR starting with `[LEGAL]`.
   * Explain why this jurisdiction is important (e.g., "High demand for AI incorporation in Estonia").
4. **Review:** A core maintainer will review your template for compliance and logic.

---

## 6. Proposing New Task Types
If you believe the protocol needs a new type of legal task (e.g., "Real Estate Title Transfer"), please open a **Discussion** in the repository rather than a PR. We must first debate the economic and security implications.

> [!NOTE]
> By contributing a template, you agree to license it under the **MIT License**, allowing the community to use and modify it freely.
