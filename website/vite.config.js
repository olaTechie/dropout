import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/dropout/',
  build: {
    target: 'es2022',
    // three.js core is ~720 kB raw (~180 kB gzipped) and cannot be
    // tree-shaken further without abandoning the @react-three stack;
    // raise the warn threshold accordingly so the build log stays signal.
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined;
          if (id.includes('/three/')) return 'three-core';
          if (
            id.includes('@react-three/fiber') ||
            id.includes('@react-three/drei') ||
            id.includes('@react-three/postprocessing')
          ) {
            return 'three-react';
          }
          if (id.includes('/d3') || id.includes('/recharts')) return 'charts';
          if (id.includes('framer-motion')) return 'motion';
          return undefined;
        },
      },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test-setup.js'],
  },
});
