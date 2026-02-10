# Proxy Protocol UI Dashboards

This directory contains standalone, single-file HTML dashboards for visualizing network activity. These UIs are designed to be lightweight, running without a build step—**React, Vue, or Angular are not required**.

---

## 1. Agent Health Dashboard (`index.html`)
* **Target Audience:** Agent Developers / Operators.
* **Purpose:** Visualizes a single Agent's spending, escrow states, and live task feed.
* **Status:** Defaults to "Simulation Mode" with mock data.

## 2. Public Status Page (`status_page.html`)
* **Target Audience:** End Users / Enterprise Clients.
* **Purpose:** Displays global network health, regional node distribution, and latency metrics.
* **Status:** Defaults to "Simulation Mode" (Connects to `GET /v1/market/ticker` in production).

---

## 🚀 How to Run

Since these are static files, you can run them immediately:

1. **Direct Open:** Double-click `index.html` or `status_page.html` to open in your browser.
2. **Local Server:**
```bash
# Run a simple Python server
python3 -m http.server
# Visit http://localhost:8000/status_page.html
```

---

## 🛠 Configuration

To connect these dashboards to real data:

1. Open the file in a text editor.
2. Locate the `<script>` tag at the bottom.
3. Replace the `setInterval` simulation loop with a `fetch()` call to your local SDK or the Proxy API.

---

## 📦 Dependencies

The dashboards utilize the following technologies:

* **Tailwind CSS:** Loaded via CDN (Internet connection required).
* **Chart.js:** Used in the Status Page for visual metrics.
* **Fonts:** Inter & Fira Code via Google Fonts.
