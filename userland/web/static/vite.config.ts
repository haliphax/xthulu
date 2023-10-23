import { resolve } from "path";
import { defineConfig } from "vite";

export default defineConfig({
	build: {
		rollupOptions: {
			input: {
				chat: resolve(__dirname, "chat/index.html"),
				index: resolve(__dirname, "index.html"),
			},
		},
		target: "esnext",
	},
});
