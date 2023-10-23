const ul: HTMLUListElement = document.getElementsByTagName("ul")[0];
const es = new EventSource("/api/chat/");

interface ChatMessage {
	user: string | null;
	message: string;
}

interface ChatToken {
	token: string;
}

let token: string;

// handle new EventSource message
es.addEventListener("message", (ev) => {
	if (!ev.data) return;

	const data: ChatMessage | ChatToken = JSON.parse(ev.data);

	// refresh CSRF token with new value
	if (Object.prototype.hasOwnProperty.call(data, "token")) {
		token = (data as ChatToken).token;
		return;
	}

	const message = data as ChatMessage;

	// append new chat message to list
	const li: HTMLLIElement = document.createElement("li");

	li.innerHTML = `
		<span class="notify ${message.user ? "user" : "system"}">
			&lt;${message.user ?? "*"}&gt;
		</span>
		<span class="message"></span>
		`;
	(li.querySelector(".message") as HTMLSpanElement)!.innerText =
		message.message;

	ul.appendChild(li);
});

const f: HTMLFormElement = document.getElementsByTagName("form")[0];
const inp: HTMLInputElement = document.getElementsByTagName("input")[0];

// handle chat message submission
f.addEventListener("submit", async (ev: SubmitEvent) => {
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
