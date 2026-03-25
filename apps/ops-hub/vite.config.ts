import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  define: {
    'process.env': {} // 🛠️ THE FIX: Prevents the browser from crashing!
  }
});
