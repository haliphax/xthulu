import { resolve } from "path";
import { defineConfig } from "vite";

export default defineConfig({
	build: {
		emptyOutDir: true,
		outDir: "../../../html",
		rollupOptions: {
			input: {
				chat: resolve(__dirname, "chat/index.html"),
				index: resolve(__dirname, "index.html"),
				logout: resolve(__dirname, "logout/index.html"),
			},
		},
		target: "esnext",
	},
});
