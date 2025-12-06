import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
      manifest: {
        name: 'IES Reader',
        short_name: 'IES Reader',
        description: 'Read books with knowledge graph integration',
        theme_color: '#FDFBF7',
        background_color: '#FDFBF7',
        display: 'standalone',
        orientation: 'any',
        scope: '/',
        start_url: '/',
        categories: ['books', 'education', 'productivity'],
        icons: [
          {
            src: '/icons/icon-192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/icons/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
          },
          {
            src: '/icons/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        // Cache strategies
        runtimeCaching: [
          {
            // Cache book files for offline reading
            urlPattern: /\/books\/\d+\/file$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'book-files',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 30, // 30 days
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            // Cache book covers
            urlPattern: /\/books\/\d+\/cover$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'book-covers',
              expiration: {
                maxEntries: 200,
                maxAgeSeconds: 60 * 60 * 24 * 7, // 7 days
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            // Network-first for API calls (book list, search, etc.)
            urlPattern: /\/api\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 10,
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60, // 1 hour
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            // Cache Google Fonts
            urlPattern: /^https:\/\/fonts\.googleapis\.com/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'google-fonts-stylesheets',
            },
          },
          {
            urlPattern: /^https:\/\/fonts\.gstatic\.com/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-webfonts',
              expiration: {
                maxEntries: 30,
                maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
        ],
        // Don't cache-bust URLs with hashes (Vite already does this)
        dontCacheBustURLsMatching: /\.[a-f0-9]{8}\./,
      },
      devOptions: {
        enabled: true, // Enable PWA in dev mode for testing
      },
    }),
  ],
  server: {
    host: true, // Expose on network for mobile testing
    proxy: {
      '/gutenberg': {
        target: 'https://www.gutenberg.org',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/gutenberg/, ''),
      },
      // Backend API proxy
      '/api': {
        target: 'http://localhost:8081',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // Books endpoint proxy
      '/books': {
        target: 'http://localhost:8081',
        changeOrigin: true,
      },
      // Graph endpoint proxy
      '/graph': {
        target: 'http://localhost:8081',
        changeOrigin: true,
      },
      // Profile endpoint proxy
      '/profile': {
        target: 'http://localhost:8081',
        changeOrigin: true,
      },
      // Question engine proxy
      '/question-engine': {
        target: 'http://localhost:8081',
        changeOrigin: true,
      },
      // Journeys proxy
      '/journeys': {
        target: 'http://localhost:8081',
        changeOrigin: true,
      },
      // Health check proxy
      '/health': {
        target: 'http://localhost:8081',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Improve chunk splitting
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'epub-vendor': ['epubjs', 'react-reader'],
        },
      },
    },
  },
})
