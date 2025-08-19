import child_process from "node:child_process";

if (process.env.ALLOW_MAIN) process.exit(0);

const branch = child_process
	.execSync("git branch --show-current")
	.toString()
	.trim();

if (branch === "main") {
	process.stderr.write("❌ Do not commit to main branch\n");
	process.exit(1);
}
