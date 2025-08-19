module.exports = {
	extends: ["gitmoji"],
	parserPreset: {
		parserOpts: {
			headerPattern: /^[^ ]+ (.*)$/,
			headerCorrespondence: ["subject"],
		},
	},
	rules: {
		"type-empty": [0, "always"],
	},
};
