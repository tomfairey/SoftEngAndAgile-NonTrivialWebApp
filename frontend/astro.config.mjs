import { defineConfig } from 'astro/config';
import node from "@astrojs/node";
import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
    integrations: [
        react()
    ],
    adapter: node({
        mode: "standalone",
    }),
    output: "server",
    server: {
        host: import.meta.env?.HOST || true,
        port: import.meta.env?.PORT || 80,
    },
    vite: {
        server: {
            watch: {
                usePolling: true,
            },
        },
    },
});