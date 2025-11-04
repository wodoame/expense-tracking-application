import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig(({ command }) => ({
  root: "frontend",
  base: command === "build" ? "/static/frontend/" : "/",
  plugins: [react()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: "bundle.js",
        manualChunks: {
          "vendor-large": ["apexcharts", "vanilla-calendar-pro"],
          "vendor-ui": ["alpinejs", "flowbite", "lit"],
        }
      }
    }
  },
  cacheDir: ".vite"
}));