// vite.config.js
import { defineConfig } from "file:///D:/Projekte/VideoRetrieval/frontend/node_modules/vite/dist/node/index.js";
import { svelte } from "file:///D:/Projekte/VideoRetrieval/frontend/node_modules/@sveltejs/vite-plugin-svelte/src/index.js";
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
      },
      external: ["chart.js"]
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFxQcm9qZWt0ZVxcXFxWaWRlb1JldHJpZXZhbFxcXFxmcm9udGVuZFwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiRDpcXFxcUHJvamVrdGVcXFxcVmlkZW9SZXRyaWV2YWxcXFxcZnJvbnRlbmRcXFxcdml0ZS5jb25maWcuanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0Q6L1Byb2pla3RlL1ZpZGVvUmV0cmlldmFsL2Zyb250ZW5kL3ZpdGUuY29uZmlnLmpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcclxuaW1wb3J0IHsgc3ZlbHRlIH0gZnJvbSAnQHN2ZWx0ZWpzL3ZpdGUtcGx1Z2luLXN2ZWx0ZSdcclxuXHJcbi8vIGh0dHBzOi8vdml0ZWpzLmRldi9jb25maWcvXHJcbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XHJcbiAgcGx1Z2luczogW3N2ZWx0ZSgpXSxcclxuICBiYXNlOiBcIi4uL1wiLCAvLyBUaGlzIHdpbGwgbWFrZSBwYXRocyByZWxhdGl2ZVxyXG4gIGJ1aWxkOiB7XHJcbiAgICAgZW1wdHlPdXREaXI6IHRydWUsXHJcbiAgICAgb3V0RGlyOiAnLi4vcHVibGljJywgLy8gV2hlcmUgd2Ugd2FudCB0byBwdXQgdGhlIGJ1aWxkXHJcbiAgICAgYXNzZXRzRGlyOiAnYXNzZXRzJywgLy8gVGhpcyB3aWxsIGJlIGZvbGRlciBpbnNpZGUgdGhlIHB1YmxpY1xyXG4gICAgIHJvbGx1cE9wdGlvbnM6IHtcclxuICAgICAgICBpbnB1dDoge1xyXG4gICAgICAgICAgIG1haW46ICcuL2luZGV4Lmh0bWwnLCAvLyBUaGlzIGluZGV4Lmh0bWwgd2lsbCBiZSBpbiBwdWJsaWMgZm9sZGVyXHJcbiAgICAgICAgICAgLy8gaWYgeW91IGhhdmUgbW9yZSBwYWdlcywganVzdCBhZGQgdGhlbSBiZWxsb3cgbGlrZSB0aGlzOlxyXG4gICAgICAgICAgIC8vIGV4YW1wbGU6ICcuL3BhZ2VzL2V4YW1wbGUuaHRtbCcsXHJcbiAgICAgICAgfSxcclxuICAgICAgICBvdXRwdXQ6IHtcclxuICAgICAgICAgICBlbnRyeUZpbGVOYW1lczogJ2Fzc2V0cy9qcy9bbmFtZV0tW2hhc2hdLmpzJywgLy8gSGVyZSB3ZSBwdXQgYWxsIGpzIGZpbGVzIGludG8ganMgZm9sZGVyXHJcbiAgICAgICAgICAgY2h1bmtGaWxlTmFtZXM6ICdhc3NldHMvanMvW25hbWVdLVtoYXNoXS5qcycsXHJcbiAgICAgICAgICAgLy8gQnV0IGFmdGVyIHRoYXQgd2UgbmVlZCB0byBkZWZpbmUgd2hpY2ggZmlsZXMgc2hvdWxkIGdvIHdoZXJlIHdpdGggcmVnZXhcclxuICAgICAgICAgICBhc3NldEZpbGVOYW1lczogKHsgbmFtZSB9KSA9PiB7XHJcbiAgICAgICAgICAgICAgaWYgKC9cXC4oZ2lmfGpwZT9nfHBuZ3xzdmcpJC8udGVzdChuYW1lID8/ICcnKSkge1xyXG4gICAgICAgICAgICAgICAgIHJldHVybiAnYXNzZXRzL2ltYWdlcy9bbmFtZV0uW2V4dF0nO1xyXG4gICAgICAgICAgICAgIH1cclxuXHJcbiAgICAgICAgICAgICAgaWYgKC9cXC5jc3MkLy50ZXN0KG5hbWUgPz8gJycpKSB7XHJcbiAgICAgICAgICAgICAgICAgcmV0dXJuICdhc3NldHMvY3NzL1tuYW1lXS1baGFzaF0uW2V4dF0nO1xyXG4gICAgICAgICAgICAgIH1cclxuXHJcbiAgICAgICAgICAgICAgcmV0dXJuICdhc3NldHMvW25hbWVdLVtoYXNoXS5bZXh0XSc7XHJcbiAgICAgICAgICAgfSxcclxuICAgICAgICB9LFxyXG4gICAgICAgIGV4dGVybmFsOiBbJ2NoYXJ0LmpzJ11cclxuICAgICB9ICAgICBcclxuICB9XHJcbn0pXHJcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBbVMsU0FBUyxvQkFBb0I7QUFDaFUsU0FBUyxjQUFjO0FBR3ZCLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQzFCLFNBQVMsQ0FBQyxPQUFPLENBQUM7QUFBQSxFQUNsQixNQUFNO0FBQUE7QUFBQSxFQUNOLE9BQU87QUFBQSxJQUNKLGFBQWE7QUFBQSxJQUNiLFFBQVE7QUFBQTtBQUFBLElBQ1IsV0FBVztBQUFBO0FBQUEsSUFDWCxlQUFlO0FBQUEsTUFDWixPQUFPO0FBQUEsUUFDSixNQUFNO0FBQUE7QUFBQTtBQUFBO0FBQUEsTUFHVDtBQUFBLE1BQ0EsUUFBUTtBQUFBLFFBQ0wsZ0JBQWdCO0FBQUE7QUFBQSxRQUNoQixnQkFBZ0I7QUFBQTtBQUFBLFFBRWhCLGdCQUFnQixDQUFDLEVBQUUsS0FBSyxNQUFNO0FBQzNCLGNBQUkseUJBQXlCLEtBQUssUUFBUSxFQUFFLEdBQUc7QUFDNUMsbUJBQU87QUFBQSxVQUNWO0FBRUEsY0FBSSxTQUFTLEtBQUssUUFBUSxFQUFFLEdBQUc7QUFDNUIsbUJBQU87QUFBQSxVQUNWO0FBRUEsaUJBQU87QUFBQSxRQUNWO0FBQUEsTUFDSDtBQUFBLE1BQ0EsVUFBVSxDQUFDLFVBQVU7QUFBQSxJQUN4QjtBQUFBLEVBQ0g7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
