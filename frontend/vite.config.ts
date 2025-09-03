import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  esbuild: {
    // Ensure proper JSX handling
    jsxDev: false,
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '127.0.0.1',
    port: 3001,
    hmr: {
      port: 3002,
      host: '127.0.0.1',
      clientPort: 3002,
      overlay: false
    },
    strictPort: false,
    open: true,
    cors: true,
    watch: {
      usePolling: true,
      interval: 100
    }
  },
  preview: {
    host: 'localhost',
    port: 3001,
  },
  define: {
    global: 'globalThis',
  },
  build: {
    commonjsOptions: {
      include: [/node_modules/],
    },
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress specific warnings
        if (warning.code === 'MODULE_LEVEL_DIRECTIVE') return;
        warn(warning);
      },
    },
  },
});
