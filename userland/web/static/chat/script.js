const ul = document.getElementsByTagName("ul")[0];
const es = new EventSource("/api/chat/");

let token;

// handle new EventSource message
es.addEventListener("message", (ev) => {
	if (!ev.data) return;

	const message = JSON.parse(ev.data);

	// refresh CSRF token with new value
	if (Object.prototype.hasOwnProperty.call(message, "token")) {
		token = message.token;
		return;
	}

	// append new chat message to list
	const li = document.createElement("li");

	li.innerHTML = `
		<span class="notify ${message.user ? "user" : "system"}">
			&lt;${message.user ?? "*"}&gt;
		</span>
		<span class="message"></span>
		`;
	li.querySelector(".message").innerText = message.message;

	ul.appendChild(li);
});

const f = document.getElementsByTagName("form")[0];
const inp = document.getElementsByTagName("input")[0];

// handle chat message submission
f.addEventListener("submit", async (ev) => {
	ev.preventDefault();
	ev.stopPropagation();

	// post to server
	await fetch("/api/chat/", {
		body: JSON.stringify({ message: inp.value, token }),
		headers: { "Content-Type": "application/json" },
		method: "POST",
	}).then(async (r) => {
		// display JSON errors and text errors
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
