"""
"Amiga" (Topaz, etc.) font codec

https://github.com/jquast/x84/blob/master/x84/encodings/amiga.py
"""

import codecs


class Codec(codecs.Codec):
    def encode(self, char, errors="strict"):
        raise NotImplementedError()

    def decode(self, char, errors="strict"):
        return codecs.charmap_decode(
            char, errors, DECODING_TABLE  # type: ignore
        )


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, char, final=False):
        raise NotImplementedError()


class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, char, final=False):
        return codecs.charmap_decode(
            char, self.errors, DECODING_TABLE  # type: ignore
        )[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getaliases():
    return (
        "amiga",
        "microknight",
        "mosoul",
        "p0tnoodle",
        "topaz",
        "topaz1",
        "topaz1plus",
        "topaz2",
        "topaz2plus",
        "topazplus",
    )


def getregentry():
    return codecs.CodecInfo(
        name="amiga",
        encode=Codec().encode,  # type: ignore
        decode=Codec().decode,  # type: ignore
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )


decoding_map = codecs.make_identity_dict(range(256))  # type: ignore
decoding_map.update(
    {
        0x002D: 0x2500,  # BOX DRAWINGS LIGHT HORIZONTAL
        0x002F: 0x2571,  # BOX DRAWINGS LIGHT DIAGONAL UPPER RIGHT TO LOWER LEFT
        0x0058: 0x2573,  # BOX DRAWINGS LIGHT DIAGONAL CROSS
        0x005C: 0x2572,  # BOX DRAWINGS LIGHT DIAGONAL UPPER LEFT TO LOWER RIGHT
        0x005F: 0x2581,  # LOWER ONE EIGHTH BLOCK
        0x007C: 0x2502,  # BOX DRAWINGS LIGHT VERTICAL
        0x007F: 0x259E,  # QUADRANT UPPER RIGHT AND LOWER LEFT
        0x0080: 0x2B1C,  # WHITE LARGE SQUARE
        0x0081: 0x2B1C,  # WHITE LARGE SQUARE
        0x0082: 0x2B1C,  # WHITE LARGE SQUARE
        0x0083: 0x2B1C,  # WHITE LARGE SQUARE
        0x0084: 0x2B1C,  # WHITE LARGE SQUARE
        0x0085: 0x2B1C,  # WHITE LARGE SQUARE
        0x0086: 0x2B1C,  # WHITE LARGE SQUARE
        0x0087: 0x2B1C,  # WHITE LARGE SQUARE
        0x0088: 0x2B1C,  # WHITE LARGE SQUARE
        0x0089: 0x2B1C,  # WHITE LARGE SQUARE
        0x008A: 0x2B1C,  # WHITE LARGE SQUARE
        0x008B: 0x2B1C,  # WHITE LARGE SQUARE
        0x008C: 0x2B1C,  # WHITE LARGE SQUARE
        0x008D: 0x2B1C,  # WHITE LARGE SQUARE
        0x008E: 0x2B1C,  # WHITE LARGE SQUARE
        0x008F: 0x2B1C,  # WHITE LARGE SQUARE
        0x0090: 0x2B1C,  # WHITE LARGE SQUARE
        0x0091: 0x2B1C,  # WHITE LARGE SQUARE
        0x0092: 0x2B1C,  # WHITE LARGE SQUARE
        0x0093: 0x2B1C,  # WHITE LARGE SQUARE
        0x0094: 0x2B1C,  # WHITE LARGE SQUARE
        0x0095: 0x2B1C,  # WHITE LARGE SQUARE
        0x0096: 0x2B1C,  # WHITE LARGE SQUARE
        0x0097: 0x2B1C,  # WHITE LARGE SQUARE
        0x0098: 0x2B1C,  # WHITE LARGE SQUARE
        0x0099: 0x2B1C,  # WHITE LARGE SQUARE
        0x009A: 0x2B1C,  # WHITE LARGE SQUARE
        0x009B: 0x2B1C,  # WHITE LARGE SQUARE
        0x009C: 0x2B1C,  # WHITE LARGE SQUARE
        0x009D: 0x2B1C,  # WHITE LARGE SQUARE
        0x009E: 0x2B1C,  # WHITE LARGE SQUARE
        0x009F: 0x2B1C,  # WHITE LARGE SQUARE
        0x00AF: 0x2594,  # UPPER ONE EIGHTH BLOCK
    }
)

DECODING_TABLE = (
    "\x00"  # 0x0000 -> NULL
    "\x01"  # 0x0001 -> START OF HEADING
    "\x02"  # 0x0002 -> START OF TEXT
    "\x03"  # 0x0003 -> END OF TEXT
    "\x04"  # 0x0004 -> END OF TRANSMISSION
    "\x05"  # 0x0005 -> ENQUIRY
    "\x06"  # 0x0006 -> ACKNOWLEDGE
    "\x07"  # 0x0007 -> BELL
    "\x08"  # 0x0008 -> BACKSPACE
    "\t"  # 0x0009 -> HORIZONTAL TABULATION
    "\n"  # 0x000a -> LINE FEED
    "\x0b"  # 0x000b -> VERTICAL TABULATION
    "\x0c"  # 0x000c -> FORM FEED
    "\r"  # 0x000d -> CARRIAGE RETURN
    "\x0e"  # 0x000e -> SHIFT OUT
    "\x0f"  # 0x000f -> SHIFT IN
    "\x10"  # 0x0010 -> DATA LINK ESCAPE
    "\x11"  # 0x0011 -> DEVICE CONTROL ONE
    "\x12"  # 0x0012 -> DEVICE CONTROL TWO
    "\x13"  # 0x0013 -> DEVICE CONTROL THREE
    "\x14"  # 0x0014 -> DEVICE CONTROL FOUR
    "\x15"  # 0x0015 -> NEGATIVE ACKNOWLEDGE
    "\x16"  # 0x0016 -> SYNCHRONOUS IDLE
    "\x17"  # 0x0017 -> END OF TRANSMISSION BLOCK
    "\x18"  # 0x0018 -> CANCEL
    "\x19"  # 0x0019 -> END OF MEDIUM
    "\x1a"  # 0x001a -> SUBSTITUTE
    "\x1b"  # 0x001b -> ESCAPE
    "\x1c"  # 0x001c -> FILE SEPARATOR
    "\x1d"  # 0x001d -> GROUP SEPARATOR
    "\x1e"  # 0x001e -> RECORD SEPARATOR
    "\x1f"  # 0x001f -> UNIT SEPARATOR
    " "  # 0x0020 -> SPACE
    "!"  # 0x0021 -> EXCLAMATION MARK
    '"'  # 0x0022 -> QUOTATION MARK
    "#"  # 0x0023 -> NUMBER SIGN
    "$"  # 0x0024 -> DOLLAR SIGN
    "%"  # 0x0025 -> PERCENT SIGN
    "&"  # 0x0026 -> AMPERSAND
    "'"  # 0x0027 -> APOSTROPHE
    "("  # 0x0028 -> LEFT PARENTHESIS
    ")"  # 0x0029 -> RIGHT PARENTHESIS
    "*"  # 0x002a -> ASTERISK
    "+"  # 0x002b -> PLUS SIGN
    ","  # 0x002c -> COMMA
    "\u2500"  # 0x002d -> BOX DRAWINGS LIGHT HORIZONTAL
    "."  # 0x002e -> FULL STOP
    "\u2571"  # 0x002f -> BOX DRAWINGS LIGHT DIAGONAL UPPER RIGHT TO LOWER LEFT
    "0"  # 0x0030 -> DIGIT ZERO
    "1"  # 0x0031 -> DIGIT ONE
    "2"  # 0x0032 -> DIGIT TWO
    "3"  # 0x0033 -> DIGIT THREE
    "4"  # 0x0034 -> DIGIT FOUR
    "5"  # 0x0035 -> DIGIT FIVE
    "6"  # 0x0036 -> DIGIT SIX
    "7"  # 0x0037 -> DIGIT SEVEN
    "8"  # 0x0038 -> DIGIT EIGHT
    "9"  # 0x0039 -> DIGIT NINE
    ":"  # 0x003a -> COLON
    ";"  # 0x003b -> SEMICOLON
    "\u27e8"  # 0x003c -> MATHEMATICAL LEFT ANGLE BRACKET
    "="  # 0x003d -> EQUALS SIGN
    "\u27e9"  # 0x003e -> MATHEMATICAL RIGHT ANGLE BRACKET
    "?"  # 0x003f -> QUESTION MARK
    "@"  # 0x0040 -> COMMERCIAL AT
    "A"  # 0x0041 -> LATIN CAPITAL LETTER A
    "B"  # 0x0042 -> LATIN CAPITAL LETTER B
    "C"  # 0x0043 -> LATIN CAPITAL LETTER C
    "D"  # 0x0044 -> LATIN CAPITAL LETTER D
    "E"  # 0x0045 -> LATIN CAPITAL LETTER E
    "F"  # 0x0046 -> LATIN CAPITAL LETTER F
    "G"  # 0x0047 -> LATIN CAPITAL LETTER G
    "H"  # 0x0048 -> LATIN CAPITAL LETTER H
    "I"  # 0x0049 -> LATIN CAPITAL LETTER I
    "J"  # 0x004a -> LATIN CAPITAL LETTER J
    "K"  # 0x004b -> LATIN CAPITAL LETTER K
    "L"  # 0x004c -> LATIN CAPITAL LETTER L
    "M"  # 0x004d -> LATIN CAPITAL LETTER M
    "N"  # 0x004e -> LATIN CAPITAL LETTER N
    "O"  # 0x004f -> LATIN CAPITAL LETTER O
    "P"  # 0x0050 -> LATIN CAPITAL LETTER P
    "Q"  # 0x0051 -> LATIN CAPITAL LETTER Q
    "R"  # 0x0052 -> LATIN CAPITAL LETTER R
    "S"  # 0x0053 -> LATIN CAPITAL LETTER S
    "T"  # 0x0054 -> LATIN CAPITAL LETTER T
    "U"  # 0x0055 -> LATIN CAPITAL LETTER U
    "V"  # 0x0056 -> LATIN CAPITAL LETTER V
    "W"  # 0x0057 -> LATIN CAPITAL LETTER W
    "\u2573"  # 0x0058 -> BOX DRAWINGS LIGHT DIAGONAL CROSS
    "Y"  # 0x0059 -> LATIN CAPITAL LETTER Y
    "Z"  # 0x005a -> LATIN CAPITAL LETTER Z
    "["  # 0x005b -> LEFT SQUARE BRACKET
    "\u2572"  # 0x005c -> BOX DRAWINGS LIGHT DIAGONAL UPPER LEFT TO LOWER RIGHT
    "]"  # 0x005d -> RIGHT SQUARE BRACKET
    "^"  # 0x005e -> CIRCUMFLEX ACCENT
    "\u2581"  # 0x005f -> LOWER ONE EIGHTH BLOCK
    "`"  # 0x0060 -> GRAVE ACCENT
    "a"  # 0x0061 -> LATIN SMALL LETTER A
    "b"  # 0x0062 -> LATIN SMALL LETTER B
    "c"  # 0x0063 -> LATIN SMALL LETTER C
    "d"  # 0x0064 -> LATIN SMALL LETTER D
    "e"  # 0x0065 -> LATIN SMALL LETTER E
    "f"  # 0x0066 -> LATIN SMALL LETTER F
    "g"  # 0x0067 -> LATIN SMALL LETTER G
    "h"  # 0x0068 -> LATIN SMALL LETTER H
    "i"  # 0x0069 -> LATIN SMALL LETTER I
    "j"  # 0x006a -> LATIN SMALL LETTER J
    "k"  # 0x006b -> LATIN SMALL LETTER K
    "l"  # 0x006c -> LATIN SMALL LETTER L
    "m"  # 0x006d -> LATIN SMALL LETTER M
    "n"  # 0x006e -> LATIN SMALL LETTER N
    "o"  # 0x006f -> LATIN SMALL LETTER O
    "p"  # 0x0070 -> LATIN SMALL LETTER P
    "q"  # 0x0071 -> LATIN SMALL LETTER Q
    "r"  # 0x0072 -> LATIN SMALL LETTER R
    "s"  # 0x0073 -> LATIN SMALL LETTER S
    "t"  # 0x0074 -> LATIN SMALL LETTER T
    "u"  # 0x0075 -> LATIN SMALL LETTER U
    "v"  # 0x0076 -> LATIN SMALL LETTER V
    "w"  # 0x0077 -> LATIN SMALL LETTER W
    "x"  # 0x0078 -> LATIN SMALL LETTER X
    "y"  # 0x0079 -> LATIN SMALL LETTER Y
    "z"  # 0x007a -> LATIN SMALL LETTER Z
    "{"  # 0x007b -> LEFT CURLY BRACKET
    "\u2502"  # 0x007c -> BOX DRAWINGS LIGHT VERTICAL
    "}"  # 0x007d -> RIGHT CURLY BRACKET
    "~"  # 0x007e -> TILDE
    "\u259e"  # 0x007f -> QUADRANT UPPER RIGHT AND LOWER LEFT
    "\u2b1c"  # 0x0080 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0081 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0082 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0083 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0084 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0085 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0086 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0087 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0088 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0089 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x008a -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x008b -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x008c -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x008d -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x008e -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x008f -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0090 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0091 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0092 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0093 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0094 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0095 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0096 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0097 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0098 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x0099 -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x009a -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x009b -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x009c -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x009d -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x009e -> WHITE LARGE SQUARE
    "\u2b1c"  # 0x009f -> WHITE LARGE SQUARE
    "\xa0"  # 0x00a0 -> NO-BREAK SPACE
    "\xa1"  # 0x00a1 -> INVERTED EXCLAMATION MARK
    "\xa2"  # 0x00a2 -> CENT SIGN
    "\xa3"  # 0x00a3 -> POUND SIGN
    "\xa4"  # 0x00a4 -> CURRENCY SIGN
    "\xa5"  # 0x00a5 -> YEN SIGN
    "\xa6"  # 0x00a6 -> BROKEN BAR
    "\xa7"  # 0x00a7 -> SECTION SIGN
    "\xa8"  # 0x00a8 -> DIAERESIS
    "\xa9"  # 0x00a9 -> COPYRIGHT SIGN
    "\xaa"  # 0x00aa -> FEMININE ORDINAL INDICATOR
    "\xab"  # 0x00ab -> LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    "\xac"  # 0x00ac -> NOT SIGN
    "\xad"  # 0x00ad -> SOFT HYPHEN
    "\xae"  # 0x00ae -> REGISTERED SIGN
    "\u2594"  # 0x00af -> UPPER ONE EIGHTH BLOCK
    "\xb0"  # 0x00b0 -> DEGREE SIGN
    "\xb1"  # 0x00b1 -> PLUS-MINUS SIGN
    "\xb2"  # 0x00b2 -> SUPERSCRIPT TWO
    "\xb3"  # 0x00b3 -> SUPERSCRIPT THREE
    "\xb4"  # 0x00b4 -> ACUTE ACCENT
    "\xb5"  # 0x00b5 -> MICRO SIGN
    "\xb6"  # 0x00b6 -> PILCROW SIGN
    "\xb7"  # 0x00b7 -> MIDDLE DOT
    "\xb8"  # 0x00b8 -> CEDILLA
    "\xb9"  # 0x00b9 -> SUPERSCRIPT ONE
    "\xba"  # 0x00ba -> MASCULINE ORDINAL INDICATOR
    "\xbb"  # 0x00bb -> RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    "\xbc"  # 0x00bc -> VULGAR FRACTION ONE QUARTER
    "\xbd"  # 0x00bd -> VULGAR FRACTION ONE HALF
    "\xbe"  # 0x00be -> VULGAR FRACTION THREE QUARTERS
    "\xbf"  # 0x00bf -> INVERTED QUESTION MARK
    "\xc0"  # 0x00c0 -> LATIN CAPITAL LETTER A WITH GRAVE
    "\xc1"  # 0x00c1 -> LATIN CAPITAL LETTER A WITH ACUTE
    "\xc2"  # 0x00c2 -> LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    "\xc3"  # 0x00c3 -> LATIN CAPITAL LETTER A WITH TILDE
    "\xc4"  # 0x00c4 -> LATIN CAPITAL LETTER A WITH DIAERESIS
    "\xc5"  # 0x00c5 -> LATIN CAPITAL LETTER A WITH RING ABOVE
    "\xc6"  # 0x00c6 -> LATIN CAPITAL LETTER AE
    "\xc7"  # 0x00c7 -> LATIN CAPITAL LETTER C WITH CEDILLA
    "\xc8"  # 0x00c8 -> LATIN CAPITAL LETTER E WITH GRAVE
    "\xc9"  # 0x00c9 -> LATIN CAPITAL LETTER E WITH ACUTE
    "\xca"  # 0x00ca -> LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    "\xcb"  # 0x00cb -> LATIN CAPITAL LETTER E WITH DIAERESIS
    "\xcc"  # 0x00cc -> LATIN CAPITAL LETTER I WITH GRAVE
    "\xcd"  # 0x00cd -> LATIN CAPITAL LETTER I WITH ACUTE
    "\xce"  # 0x00ce -> LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    "\xcf"  # 0x00cf -> LATIN CAPITAL LETTER I WITH DIAERESIS
    "\xd0"  # 0x00d0 -> LATIN CAPITAL LETTER ETH
    "\xd1"  # 0x00d1 -> LATIN CAPITAL LETTER N WITH TILDE
    "\xd2"  # 0x00d2 -> LATIN CAPITAL LETTER O WITH GRAVE
    "\xd3"  # 0x00d3 -> LATIN CAPITAL LETTER O WITH ACUTE
    "\xd4"  # 0x00d4 -> LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    "\xd5"  # 0x00d5 -> LATIN CAPITAL LETTER O WITH TILDE
    "\xd6"  # 0x00d6 -> LATIN CAPITAL LETTER O WITH DIAERESIS
    "\xd7"  # 0x00d7 -> MULTIPLICATION SIGN
    "\xd8"  # 0x00d8 -> LATIN CAPITAL LETTER O WITH STROKE
    "\xd9"  # 0x00d9 -> LATIN CAPITAL LETTER U WITH GRAVE
    "\xda"  # 0x00da -> LATIN CAPITAL LETTER U WITH ACUTE
    "\xdb"  # 0x00db -> LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    "\xdc"  # 0x00dc -> LATIN CAPITAL LETTER U WITH DIAERESIS
    "\xdd"  # 0x00dd -> LATIN CAPITAL LETTER Y WITH ACUTE
    "\xde"  # 0x00de -> LATIN CAPITAL LETTER THORN
    "\xdf"  # 0x00df -> LATIN SMALL LETTER SHARP S
    "\xe0"  # 0x00e0 -> LATIN SMALL LETTER A WITH GRAVE
    "\xe1"  # 0x00e1 -> LATIN SMALL LETTER A WITH ACUTE
    "\xe2"  # 0x00e2 -> LATIN SMALL LETTER A WITH CIRCUMFLEX
    "\xe3"  # 0x00e3 -> LATIN SMALL LETTER A WITH TILDE
    "\xe4"  # 0x00e4 -> LATIN SMALL LETTER A WITH DIAERESIS
    "\xe5"  # 0x00e5 -> LATIN SMALL LETTER A WITH RING ABOVE
    "\xe6"  # 0x00e6 -> LATIN SMALL LETTER AE
    "\xe7"  # 0x00e7 -> LATIN SMALL LETTER C WITH CEDILLA
    "\xe8"  # 0x00e8 -> LATIN SMALL LETTER E WITH GRAVE
    "\xe9"  # 0x00e9 -> LATIN SMALL LETTER E WITH ACUTE
    "\xea"  # 0x00ea -> LATIN SMALL LETTER E WITH CIRCUMFLEX
    "\xeb"  # 0x00eb -> LATIN SMALL LETTER E WITH DIAERESIS
    "\xec"  # 0x00ec -> LATIN SMALL LETTER I WITH GRAVE
    "\xed"  # 0x00ed -> LATIN SMALL LETTER I WITH ACUTE
    "\xee"  # 0x00ee -> LATIN SMALL LETTER I WITH CIRCUMFLEX
    "\xef"  # 0x00ef -> LATIN SMALL LETTER I WITH DIAERESIS
    "\xf0"  # 0x00f0 -> LATIN SMALL LETTER ETH
    "\xf1"  # 0x00f1 -> LATIN SMALL LETTER N WITH TILDE
    "\xf2"  # 0x00f2 -> LATIN SMALL LETTER O WITH GRAVE
    "\xf3"  # 0x00f3 -> LATIN SMALL LETTER O WITH ACUTE
    "\xf4"  # 0x00f4 -> LATIN SMALL LETTER O WITH CIRCUMFLEX
    "\xf5"  # 0x00f5 -> LATIN SMALL LETTER O WITH TILDE
    "\xf6"  # 0x00f6 -> LATIN SMALL LETTER O WITH DIAERESIS
    "\xf7"  # 0x00f7 -> DIVISION SIGN
    "\xf8"  # 0x00f8 -> LATIN SMALL LETTER O WITH STROKE
    "\xf9"  # 0x00f9 -> LATIN SMALL LETTER U WITH GRAVE
    "\xfa"  # 0x00fa -> LATIN SMALL LETTER U WITH ACUTE
    "\xfb"  # 0x00fb -> LATIN SMALL LETTER U WITH CIRCUMFLEX
    "\xfc"  # 0x00fc -> LATIN SMALL LETTER U WITH DIAERESIS
    "\xfd"  # 0x00fd -> LATIN SMALL LETTER Y WITH ACUTE
    "\xfe"  # 0x00fe -> LATIN SMALL LETTER THORN
    "\xff"  # 0x00ff -> LATIN SMALL LETTER Y WITH DIAERESIS
)
