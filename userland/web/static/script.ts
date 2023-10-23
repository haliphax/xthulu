class DemoResponse {
	userland!: true;
	whoami!: string;
}

(async () => {
	await fetch("/api/")
		.then((r) => r.json())
		.then((d: DemoResponse) => {
			if (d.userland !== true) throw "Unexpected response";
			document.getElementById("connect")!.innerHTML = "connected!";
			const p = document.createElement("p");
			p.innerHTML = `Welcome, <strong>${d.whoami}</strong>!`;
			document.body.appendChild(p);
		})
		.catch(() => {
			document.getElementById("connect")!.innerHTML = "disconnected?!";
		});
})();
