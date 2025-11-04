import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: 'core/static/js/vite', 
    rollupOptions: {
      output: {
        entryFileNames: 'bundle.js', 
        manualChunks: {
          'vendor-large': ['apexcharts', 'vanilla-calendar-pro'], // Large libraries
          'vendor-ui': ['alpinejs', 'flowbite', 'lit'], // UI libraries
        }
      }
    }
  }, 
  cacheDir: '.vite'
});