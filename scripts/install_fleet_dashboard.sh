#!/bin/bash

# PROXY PROTOCOL - FLEET DASHBOARD INSTALLER (v1.0)
# "Deploy the Command Center in seconds."
# ----------------------------------------------------
# Usage: ./install_fleet_dashboard.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}___  ____  ____  ____  __  __${NC}"
echo -e "${GREEN}__ \/ __ \/ __ \/ \/  \/ / / /${NC}"
echo -e "${GREEN}___/ /_/ / /_/ /    / /_/ / ${NC}"
echo -e "${GREEN}   \____/\____/_/\_/\__, /  ${NC}"
echo -e "${GREEN}FLEET DASHBOARD SETUP /____/    ${NC}"
echo ""

# 1. Prerequisite Check
echo -e "${BLUE}[*] Checking prerequisites...${NC}"
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v18+."
    exit 1
fi
echo "   -> Node.js detected."

# 2. Project Scaffolding
TARGET_DIR="proxy-fleet-ui"
echo -e "${BLUE}[*] Creating project directory: ${TARGET_DIR}...${NC}"
mkdir -p $TARGET_DIR
cd $TARGET_DIR

# 3. Initialize Package
echo -e "${BLUE}[*] Initializing package.json...${NC}"
cat > package.json <<EOF
{
  "name": "proxy-fleet-dashboard",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.300.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "vite": "^5.0.8"
  }
}
EOF

# 4. Install Dependencies
echo -e "${BLUE}[*] Installing dependencies (this may take a minute)...${NC}"
npm install

# 5. Configuration Files
echo -e "${BLUE}[*] Writing configuration files...${NC}"

# Tailwind Config
cat > tailwind.config.js <<EOF
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

# PostCSS Config
cat > postcss.config.js <<EOF
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# Vite Config
cat > vite.config.js <<EOF
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Expose to local network
    port: 3000
  }
})
EOF

# 6. Source Code Structure
echo -e "${BLUE}[*] Creating source structure...${NC}"
mkdir -p src

# Entry Point (main.jsx)
cat > src/main.jsx <<EOF
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
EOF

# CSS (index.css)
cat > src/index.css <<EOF
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #050505;
  color: #e5e5e5;
}
EOF

# HTML Entry (index.html)
cat > index.html <<EOF
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Proxy Fleet Command</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
EOF

# 7. Inject Dashboard Code
# We check if the jsx file exists in the parent repo, otherwise create a placeholder.
SOURCE_JSX="../../node_fleet_dashboard.jsx"
if [ -f "$SOURCE_JSX" ]; then
    echo -e "${BLUE}[*] Copying dashboard code from repository...${NC}"
    cp "$SOURCE_JSX" src/App.jsx
else
    echo -e "${BLUE}[*] Source JSX not found in parent directory. Creating placeholder...${NC}"
    echo -e "    -> ⚠️  Please paste the content of 'node_fleet_dashboard.jsx' into '$TARGET_DIR/src/App.jsx'"
    
    cat > src/App.jsx <<EOF
import React from 'react';
export default function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-black text-green-500 font-mono">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">FLEET COMMAND INSTALLED</h1>
        <p>Please overwrite src/App.jsx with the code from node_fleet_dashboard.jsx</p>
      </div>
    </div>
  );
}
EOF
fi

echo ""
echo -e "${GREEN}✅ INSTALLATION COMPLETE${NC}"
echo "------------------------------------------------"
echo "To start the dashboard:"
echo "  cd $TARGET_DIR"
echo "  npm run dev"
echo ""
echo "Access via: http://localhost:3000"
echo "------------------------------------------------"
