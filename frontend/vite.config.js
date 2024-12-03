import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))  // Alias for simpler imports
    },
  },
  define: {
    'process.env': {
      VITE_API_BASE_URL: process.env.VITE_API_BASE_URL,  // Use environment variable for API base URL
    }
  },
})
