import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import react from '@astrojs/react';

// Determine base path based on environment
// In development, use '/' for easier local testing
// In production (build), use '/' for shrey.github.io (root domain)
const isDev = process.env.NODE_ENV !== 'production' && !process.env.CI;

// https://astro.build/config
export default defineConfig({
  integrations: [tailwind(), react()],
  site: 'https://shr-chauhan.github.io',
  // Base path is '/' for both dev and production since we're deploying to the root domain
  base: '/',
  // Use hybrid mode: API routes work in dev, but pages are static for GitHub Pages
  // For production, use the separate Python backend (set PUBLIC_CHAT_API_URL)
  output: 'hybrid',
});

