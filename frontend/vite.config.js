import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/interview': 'http://127.0.0.1:8000',
      '/resume': 'http://127.0.0.1:8000',
      '/submit-audio-answer': 'http://127.0.0.1:8000',
    },
  },
})
