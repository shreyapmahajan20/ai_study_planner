import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/planner': 'http://localhost:8000',
      '/syllabus': 'http://localhost:8000',
      '/academic-profile': 'http://localhost:8000',
      '/profile': 'http://localhost:8000',
    },
  },
})
