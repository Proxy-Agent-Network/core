# Agent Health Dashboard (UI Example)

A standalone, single-file HTML dashboard for visualizing Agent performance, escrow states, and reputation metrics.

---

## 🚀 How to Run

Since this is a static HTML file with no build step required, you can run it in two ways:

1. **Direct Open:** Simply double-click `index.html` to open it in your browser.
2. **Local Server:** Run the following command in this directory and visit `http://localhost:8000`:

```bash
python3 -m http.server
```

---

## 🛠 Configuration

By default, the dashboard runs in **Simulation Mode**. It generates synthetic data to demonstrate various UI states such as Success, Warning, and Transactions.

### Connecting to Real Data
To connect the dashboard to your live Agent or the Sandbox environment:

1. Open `index.html` in a text editor.
2. Locate the `<script>` tag at the bottom of the file.
3. Replace the `setInterval` simulation loop with a `fetch()` call to your local SDK or the Proxy API.

---

## 📦 Dependencies

This project utilizes the following technologies:

* **Tailwind CSS:** Loaded via CDN (Internet connection required).
* **Fonts:** [Fira Code](https://github.com/tonsky/FiraCode) via Google Fonts.
