import { sites } from '@openai/sites-vite-plugin';
import vinext from 'vinext';
import { defineConfig } from 'vite';
// Portable static website without a server runtime or hosting-specific bindings.
export default defineConfig({ plugins: [vinext(), sites()] });
