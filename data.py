"""
The data module encapsulates all static data to represent a single source of truth
for all other modules
"""

import re


def compile_map_pattern(d: dict[str, str]) -> re.Pattern:
    keys = (re.escape(k) for k in d.keys())
    return re.compile(r"\b(" + "|".join(keys) + r")\b")


def sub_map_pattern(pattern, d: dict[str, str], s: str) -> str:
    return pattern.sub(lambda x: d[x.group()], s)


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

short_vowels = fatha + damma + kasra + fathatan + dammatan + kasratan
harakat_wo_shaddah = short_vowels + sukun
long_vowels = alif + waw + ya
half_vowels = waw + ya

half_vowel_map = {
    "و": "w",
    "ي": "y",
}

subs = {
    alif_maksurah: alif,
    "[\u0622-\u0626\u0671-\u0676\u0678]": hamza,
    "(.)" + shaddah: lambda match: match.group(1) * 2,
}

diacritic_map = {
    **{
        rf"{half_vowel}(?={harakah})": latin_half_vowel
        for harakah in harakat_wo_shaddah
        for half_vowel, latin_half_vowel in half_vowel_map.items()
    },
    fatha + alif: "ā",
    damma + waw: "ū",
    kasra + ya: "ī",
    fatha: "a",
    damma: "u",
    kasra: "i",
    fathatan: "an",
    dammatan: "un",
    kasratan: "in",
    alif + fathatan + "$": "an",
    fathatan + alif + "$": "an",
    sukun: "",
}

char_map = {
    "^" + hamza: "",
    hamza: "ʾ",
    alif: "a",
    "ب": "b",
    "ت": "t",
    "ة": "t",  # this is the default. Should be overriden
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
    **half_vowel_map,
}

special_char_map = {"ﷲ": "allah"}

# Not currently necessary
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

# Pattern to match an arabic word
token_pattern = re.compile("[\u0621-\u0655]+")

conjunction_prefixes = {
    "ف": "fa",
    "و": "wa",
}
preposition_prefixes = {
    "ب": "bi",
    "ك": "ka",
    "ل": "li",
    "في": "fi",
}
article_prefixes = {
    "ال": "al",
    "الْ": "al",
    "أَلْ": "al",
}
prefixes = conjunction_prefixes | preposition_prefixes | article_prefixes
prefix_lengths = sorted({len(x) for x in prefixes}, reverse=True)

sentence_stop_marks = ".!?\n"
after_map = {
    "۔": ".",
    "؟": "?",
    "،": ",",
}
after_map_pattern = compile_map_pattern(after_map)
