import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// In development, calls to /api are forwarded to the FastAPI backend, so there are no CORS problems.
// Change the backend address by creating dashboard/.env with  VITE_API_URL=http://192.168.x.x:8000
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: { '/api': { target: env.VITE_API_URL || 'http://127.0.0.1:8000', changeOrigin: true } },
    },
  };
});
