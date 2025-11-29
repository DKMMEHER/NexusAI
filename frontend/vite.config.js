import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      '/text_to_video': 'http://127.0.0.1:8002',
      '/image_to_video': 'http://127.0.0.1:8002',
      '/video_from_reference_images': 'http://127.0.0.1:8002',
      '/video_from_first_last_frames': 'http://127.0.0.1:8002',
      '/extend_veo_video': 'http://127.0.0.1:8002',
      '/status': 'http://127.0.0.1:8002',
      '/download': 'http://127.0.0.1:8002',
      '/image': 'http://127.0.0.1:8000',
      '/summarize': 'http://127.0.0.1:8003',
      '/transcript': 'http://127.0.0.1:8004',
      '/chat': 'http://127.0.0.1:8005',
      '/api/documents': {
        target: 'http://127.0.0.1:8003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/documents/, '')
      },
      '/api/youtube': {
        target: 'http://127.0.0.1:8004',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/youtube/, '')
      },
      '/api/chat': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/chat/, '')
      },
    }
  }
})
