import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [tailwindcss()],
  resolve: { alias: { "@": path.resolve(__dirname, "./static/js") } },
  base: "/static/",
  build: {
    minify: true,
    manifest: true,
    outDir: path.resolve(__dirname, "./static/dist"),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        styles: path.resolve(__dirname, "./static/css/styles.css"),
        main: path.resolve(__dirname, "./static/js/main.js"),
      },
      output: {
        entryFileNames: `js/[name]-[hash].js`,
        chunkFileNames: `js/[name]-[hash].js`,
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith(".css")) {
            return `css/[name]-[hash][extname]`;
          }
          if (assetInfo.name?.match(/\.(woff2?|eot|ttf|otf|svg)$/)) {
            return `fonts/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        },
      },
    },
  },
  server: {
    port: parseInt(process.env.DJANGO_VITE_SERVER_PORT || "5173"),
    strictPort: true,
    hmr: {
      host: process.env.DJANGO_VITE_SERVER_HOST || "localhost",
      protocol: "ws",
    },
    watch: {
      ignored: ["**/.venv/**", "**/node_modules/**", "**/.git/**"],
    },
  },
});
