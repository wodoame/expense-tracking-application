import { defineConfig } from "vite";
export default defineConfig({
  build: {
    outDir: 'core/static/js/vite', 
    rollupOptions: {
      output: {
        entryFileNames: 'bundle.js'
      }
    }
  }
});