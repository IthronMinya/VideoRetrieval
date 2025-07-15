import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import envCompatible from 'vite-plugin-env-compatible';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte(), envCompatible()],
  base: "../", // This will make paths relative
  build: {
     emptyOutDir: true,
     outDir: '../public', // Where we want to put the build
     assetsDir: 'assets', // This will be folder inside the public
     rollupOptions: {
        input: {
           main: './index.html', // This index.html will be in public folder
           // if you have more pages, just add them bellow like this:
           // example: './pages/example.html',
        },
        output: {
           entryFileNames: 'assets/js/[name]-[hash].js', // Here we put all js files into js folder
           chunkFileNames: 'assets/js/[name]-[hash].js',
           // But after that we need to define which files should go where with regex
           assetFileNames: ({ name }) => {
              if (/\.(gif|jpe?g|png|svg)$/.test(name ?? '')) {
                 return 'assets/images/[name].[ext]';
              }

              if (/\.css$/.test(name ?? '')) {
                 return 'assets/css/[name]-[hash].[ext]';
              }

              return 'assets/[name]-[hash].[ext]';
           },
        },
        external: ['chart.js']
     }     
  }
})
