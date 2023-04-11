"""Console management constants"""

ZWNJ = "\u200c"
"""Zero-width non-joiner; blocks next grapheme from joining with cluster"""

ZWJ = "\u200d"
"""Zero-width joiner; joins next grapheme with cluster"""

VARIATION_SELECTORS = set((chr(c) for c in range(0xFE00, 0xFE0F + 1)))
"""Variation selectors; modify display of previous grapheme"""

EMOJI_VS = "\ufe0f"
"""'Emoji type' variation selector; display previous character as emoji"""

SKIN_TONES = set((chr(c) for c in range(0x1F3FB, 0x1F3FF + 1)))
"""Skin tone modifiers; modifies previous emoji with no ZWJ between"""

KEYCAP = "\u20e3"
"""Key cap modifier; modifies previous character with no ZWJ between"""

MODIFIERS = SKIN_TONES | set(KEYCAP)
"""Set of all supported base modifiers"""

ASSUME_WIDE = False
"""
Whether to assume that all emoji matched by `is_emoji()` are Wide, even if their
`unicodedata.east_asian_width()` result is Narrow
"""

FORCE_EVS_WIDE = True
"""
Whether Narrow emoji which are joined by the Emoji Variation Selector `\\ufe0f`
will be forcibly labeled as Wide for the purposes of column offset compensation
(e.g. varation-selected male/female symbol emoji)
"""

VALID_ZWC = set(("\n"))
"""Unjoined zero-width characters that will not be stripped during parsing"""
