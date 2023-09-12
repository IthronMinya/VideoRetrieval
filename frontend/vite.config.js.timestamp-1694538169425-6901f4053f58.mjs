// vite.config.js
import { defineConfig } from "file:///D:/VideoRetrieval/frontend/node_modules/vite/dist/node/index.js";
import { svelte } from "file:///D:/VideoRetrieval/frontend/node_modules/@sveltejs/vite-plugin-svelte/src/index.js";
var vite_config_default = defineConfig({
  plugins: [svelte()],
  base: "../",
  // This will make paths relative
  build: {
    emptyOutDir: true,
    outDir: "../public",
    // Where we want to put the build
    assetsDir: "assets",
    // This will be folder inside the public
    rollupOptions: {
      input: {
        main: "./index.html"
        // This index.html will be in public folder
        // if you have more pages, just add them bellow like this:
        // example: './pages/example.html',
      },
      output: {
        entryFileNames: "assets/js/[name]-[hash].js",
        // Here we put all js files into js folder
        chunkFileNames: "assets/js/[name]-[hash].js",
        // But after that we need to define which files should go where with regex
        assetFileNames: ({ name }) => {
          if (/\.(gif|jpe?g|png|svg)$/.test(name ?? "")) {
            return "assets/images/[name].[ext]";
          }
          if (/\.css$/.test(name ?? "")) {
            return "assets/css/[name]-[hash].[ext]";
          }
          return "assets/[name]-[hash].[ext]";
        }
      }
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFxWaWRlb1JldHJpZXZhbFxcXFxmcm9udGVuZFwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiRDpcXFxcVmlkZW9SZXRyaWV2YWxcXFxcZnJvbnRlbmRcXFxcdml0ZS5jb25maWcuanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0Q6L1ZpZGVvUmV0cmlldmFsL2Zyb250ZW5kL3ZpdGUuY29uZmlnLmpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB7IHN2ZWx0ZSB9IGZyb20gJ0BzdmVsdGVqcy92aXRlLXBsdWdpbi1zdmVsdGUnXG5cbi8vIGh0dHBzOi8vdml0ZWpzLmRldi9jb25maWcvXG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoe1xuICBwbHVnaW5zOiBbc3ZlbHRlKCldLFxuICBiYXNlOiBcIi4uL1wiLCAvLyBUaGlzIHdpbGwgbWFrZSBwYXRocyByZWxhdGl2ZVxuICBidWlsZDoge1xuICAgICBlbXB0eU91dERpcjogdHJ1ZSxcbiAgICAgb3V0RGlyOiAnLi4vcHVibGljJywgLy8gV2hlcmUgd2Ugd2FudCB0byBwdXQgdGhlIGJ1aWxkXG4gICAgIGFzc2V0c0RpcjogJ2Fzc2V0cycsIC8vIFRoaXMgd2lsbCBiZSBmb2xkZXIgaW5zaWRlIHRoZSBwdWJsaWNcbiAgICAgcm9sbHVwT3B0aW9uczoge1xuICAgICAgICBpbnB1dDoge1xuICAgICAgICAgICBtYWluOiAnLi9pbmRleC5odG1sJywgLy8gVGhpcyBpbmRleC5odG1sIHdpbGwgYmUgaW4gcHVibGljIGZvbGRlclxuICAgICAgICAgICAvLyBpZiB5b3UgaGF2ZSBtb3JlIHBhZ2VzLCBqdXN0IGFkZCB0aGVtIGJlbGxvdyBsaWtlIHRoaXM6XG4gICAgICAgICAgIC8vIGV4YW1wbGU6ICcuL3BhZ2VzL2V4YW1wbGUuaHRtbCcsXG4gICAgICAgIH0sXG4gICAgICAgIG91dHB1dDoge1xuICAgICAgICAgICBlbnRyeUZpbGVOYW1lczogJ2Fzc2V0cy9qcy9bbmFtZV0tW2hhc2hdLmpzJywgLy8gSGVyZSB3ZSBwdXQgYWxsIGpzIGZpbGVzIGludG8ganMgZm9sZGVyXG4gICAgICAgICAgIGNodW5rRmlsZU5hbWVzOiAnYXNzZXRzL2pzL1tuYW1lXS1baGFzaF0uanMnLFxuICAgICAgICAgICAvLyBCdXQgYWZ0ZXIgdGhhdCB3ZSBuZWVkIHRvIGRlZmluZSB3aGljaCBmaWxlcyBzaG91bGQgZ28gd2hlcmUgd2l0aCByZWdleFxuICAgICAgICAgICBhc3NldEZpbGVOYW1lczogKHsgbmFtZSB9KSA9PiB7XG4gICAgICAgICAgICAgIGlmICgvXFwuKGdpZnxqcGU/Z3xwbmd8c3ZnKSQvLnRlc3QobmFtZSA/PyAnJykpIHtcbiAgICAgICAgICAgICAgICAgcmV0dXJuICdhc3NldHMvaW1hZ2VzL1tuYW1lXS5bZXh0XSc7XG4gICAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgICBpZiAoL1xcLmNzcyQvLnRlc3QobmFtZSA/PyAnJykpIHtcbiAgICAgICAgICAgICAgICAgcmV0dXJuICdhc3NldHMvY3NzL1tuYW1lXS1baGFzaF0uW2V4dF0nO1xuICAgICAgICAgICAgICB9XG5cbiAgICAgICAgICAgICAgcmV0dXJuICdhc3NldHMvW25hbWVdLVtoYXNoXS5bZXh0XSc7XG4gICAgICAgICAgIH0sXG4gICAgICAgIH1cbiAgICAgfSAgICAgXG4gIH1cbn0pXG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQXNRLFNBQVMsb0JBQW9CO0FBQ25TLFNBQVMsY0FBYztBQUd2QixJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixTQUFTLENBQUMsT0FBTyxDQUFDO0FBQUEsRUFDbEIsTUFBTTtBQUFBO0FBQUEsRUFDTixPQUFPO0FBQUEsSUFDSixhQUFhO0FBQUEsSUFDYixRQUFRO0FBQUE7QUFBQSxJQUNSLFdBQVc7QUFBQTtBQUFBLElBQ1gsZUFBZTtBQUFBLE1BQ1osT0FBTztBQUFBLFFBQ0osTUFBTTtBQUFBO0FBQUE7QUFBQTtBQUFBLE1BR1Q7QUFBQSxNQUNBLFFBQVE7QUFBQSxRQUNMLGdCQUFnQjtBQUFBO0FBQUEsUUFDaEIsZ0JBQWdCO0FBQUE7QUFBQSxRQUVoQixnQkFBZ0IsQ0FBQyxFQUFFLEtBQUssTUFBTTtBQUMzQixjQUFJLHlCQUF5QixLQUFLLFFBQVEsRUFBRSxHQUFHO0FBQzVDLG1CQUFPO0FBQUEsVUFDVjtBQUVBLGNBQUksU0FBUyxLQUFLLFFBQVEsRUFBRSxHQUFHO0FBQzVCLG1CQUFPO0FBQUEsVUFDVjtBQUVBLGlCQUFPO0FBQUEsUUFDVjtBQUFBLE1BQ0g7QUFBQSxJQUNIO0FBQUEsRUFDSDtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
