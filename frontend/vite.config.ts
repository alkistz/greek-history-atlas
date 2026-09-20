import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		sveltekit({
			compilerOptions: {
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			// No server: every page is client-rendered (`ssr = false`) and every route
			// is dynamic, so the whole site is one fallback shell plus the API export.
			adapter: adapter({ fallback: 'index.html' })
		})
	],
	server: {
		// The backend. Proxying keeps every fetch a relative /api/... path, so no
		// absolute URLs in the code and no CORS to think about.
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true,
				// The deployed site fetches the files `make export` wrote
				// (/api/events.json); FastAPI serves the same bytes at /api/events.
				// Stripping the suffix here lets one set of URLs work in both places.
				rewrite: (path) => path.replace(/\.json$/, '')
			}
		}
	}
});
