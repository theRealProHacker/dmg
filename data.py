"""
The data module encapsulates all static data to represent a single source of truth
for all other modules
"""

# TODO: use pyarabic.araby constants

alif = "\u0627"
waw = "\u0648"
alif_maksurah = "\u0649"
ya = "\u064A"
fathatan = "\u064B"
dammatan = "\u064C"
kasratan = "\u064D"
fatha = "\u064E"
damma = "\u064F"
kasra = "\u0650"
shaddah = "\u0651"
sukun = "\u0652"
hamza = "\u0621"
alif_maddah = "\u0622"


subs = {
    alif_maksurah: alif,
    # TODO: add more hamza rules
    "أ": hamza,
}

diacritic_map = {
    fatha + alif: "ā",
    damma + waw: "ū",
    kasra + ya: "ī",
    fatha: "a",
    damma: "u",
    kasra: "i",
    fathatan: "an",
    dammatan: "un",
    kasratan: "in",
    # This is because an alif might be added
    alif + fathatan + "$": "an",
    fathatan + alif + "$": "an",
    "(.)" + shaddah: lambda match: match.group(1) * 2,
    sukun: "",
}

char_map = {
    "^" + hamza: "",
    hamza: "ʾ",
    alif: "a",
    "ب": "b",
    "ت": "t",
    "ث": "ṯ",
    "ج": "ǧ",
    "ح": "ḥ",
    "خ": "ḫ",
    "د": "d",
    "ذ": "ḏ",
    "ر": "r",
    "ز": "z",
    "س": "s",
    "ش": "š",
    "ص": "ṣ",
    "ض": "ḍ",
    "ط": "ṭ",
    "ظ": "ẓ",
    "ع": "ʿ",
    "غ": "ġ",
    "ف": "f",
    "ق": "q",
    "ك": "k",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "ه": "h",
    # TODO: make them long when following a consonant
    # TODO: nisba suffix
    "و": "w",
    "ي": "y",
}

special_char_map = {"ﷲ": "allah"}

pausa_map = {
    "[" + fatha + damma + kasra + fathatan + dammatan + kasratan + shaddah + "]$": "",
    fathatan + alif + "$": alif,
    alif + fathatan + "$": alif,
}


sun_letters = {"ت", "ث", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ن"}

# latin sun letters
sun_letters = set("tṯdḏrzsšṣḍṭẓn")

# print([
#     "|".join(hex(ord(x)) for x in arab) for arab in char_map|diacritic_map
# ])


latin_prefixes = {"al"}

# latin_prefix_lengths = {len(p) for p in prefixes}
