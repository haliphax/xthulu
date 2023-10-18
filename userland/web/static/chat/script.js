const ul = document.getElementsByTagName("ul")[0];
const es = new EventSource("/api/user/chat/");

es.addEventListener("message", (ev) => {
	if (!ev.data) return;

	const message = JSON.parse(ev.data);
	const li = document.createElement("li");

	li.innerHTML = `
		<span class="notify ${message.user ? "user" : "system"}">
			&lt;${message.user ?? "*"}&gt;
		</span>
		<span class="message">${message.message}</span>
		`;

	ul.appendChild(li);
});

const f = document.getElementsByTagName("form")[0];
const inp = document.getElementsByTagName("input")[0];

f.addEventListener("submit", async (ev) => {
	ev.preventDefault();
	ev.stopPropagation();

	await fetch("/api/user/chat/", {
		body: JSON.stringify({ message: inp.value }),
		headers: { "Content-Type": "application/json" },
		method: "POST",
	}).then(async (r) => {
		if (r.status != 200) {
			try {
				alert(await r.json().then((v) => `Error: ${v.detail}`));
			} catch (ex) {
				alert(await r.text());
			}

			return;
		}

		inp.value = "";
	});

	return false;
});
