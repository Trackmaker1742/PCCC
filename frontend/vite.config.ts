import { defineConfig } from 'vite';

export default defineConfig({
  base: '/static/dist/',
  // The Vite dev server proxies API calls to the FastAPI backend.
  // When building for production the output lands in ../static/dist
  // which is served by FastAPI under /static/dist/.
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/stored_files': 'http://127.0.0.1:8000',
    },
  },
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
  },
});
