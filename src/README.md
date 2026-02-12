# Proxy Protocol Frontend Suite

This directory contains the human-facing interfaces for the Proxy Protocol. To ensure compatibility with hardware-attested nodes and air-gapped environments, all UIs in this directory must adhere to the **Monolithic Portal Standard**.

---

## 1. Directory Structure

| Path | Description |
| :--- | :--- |
| `/common` | Shared logic, TypeScript interfaces, and protocol-wide constants. |
| `/components` | Reusable UI atoms (Gavel icons, status indicators, terminal-themed wrappers). |
| `/portals` | High-fidelity, self-contained dashboards for specific network roles. |

---

## 2. The Monolithic Portal Standard

Every file in `/portals` (e.g., `JuryPortal.jsx`, `FleetCommand.jsx`) must be a **Single-File Monolith**.

### Requirements:
* **Zero External JS/CSS Dependencies:** All logic, state management, and styling (via Tailwind or inline CSS) must reside within the single `.jsx` or `.html` file.
* **Portability:** A portal should be capable of running via a simple Python `http.server` or embedded directly into a FastAPI template without a build step.
* **Security Auditability:** Auditors must be able to verify the entire data flow of a portal in a single continuous scroll to ensure no PII (Personally Identifiable Information) leaks or unauthorized API calls exist.

---

## 3. Development Guidelines

### Design Language: "Industrial Terminal"
* **Palette:** Void Black (`#050505`) backgrounds with high-contrast accents (Terminal Green, Signal Red, Indigo).
* **Typography:** Monospaced fonts for data (Fira Code/Roboto Mono), clean Sans-Serif for body text (Inter).
* **Feedback:** Use animated pulse indicators for live hardware heartbeats and "Terminal Logs" for background processes.

### State Management
* **Local State First:** Favor `useState` and `useEffect` for individual portals.
* **E2EE Tunnels:** Ensure all messaging components within portals support **RSA-OAEP / SHA-256** encryption as defined in the `authentication.md` spec.

---

## 4. Deployment

Portals can be deployed independently or served via the `core/scripts/install_fleet_dashboard.sh` orchestrator.

> *“Organize for humans; optimize for silicon.”*
