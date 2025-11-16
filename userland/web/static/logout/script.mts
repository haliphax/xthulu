await fetch("/api/logout/").then((r) => {
	if (r.status !== 401) {
		document.getElementById("status")!.innerHTML =
			`There was an error. Status code: ${r.status}`;
		return;
	}

	document.getElementById("status")!.innerHTML =
		"You have been logged out successfully.";
});
