"""
The data module encapsulates all static data to represent a single source of truth
for all other modules
"""

import re


def compile_single_char_map_pattern(d: dict[str, str]) -> re.Pattern:
    return re.compile(f"[{''.join(d)}]")


def compile_map_pattern(d: dict[str, str]) -> re.Pattern:
    return re.compile("|".join(re.escape(x) for x in d))


def sub_map_pattern(pattern, d: dict[str, str], s: str) -> str:
    return pattern.sub(lambda x: d[x.group()], s)


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
alif_wasl = "ٱ"

short_vowels = fatha + damma + kasra + fathatan + dammatan + kasratan
harakat_wo_shaddah = short_vowels + sukun
long_vowels = alif + waw + ya
half_vowels = waw + ya
half_vowels_as_consonants = "wy"
half_vowels_as_vowels = "ūī"
half_vowels_as_short_vowels = "ui"

unicode_cleanup_map = {
    # replace ligatures and presentation forms with their components
    # https://en.wikipedia.org/wiki/Arabic_script_in_Unicode#Compact_table
    # Mostly: https://en.wikipedia.org/wiki/Arabic_Presentation_Forms-B
    **{
        "ﭐ": alif_wasl,
        "ﭑ": alif_wasl,
        "ﮪ": "ه",
        "ﮫ": "ه",
        "ﮬ": "ه",
        "ﮭ": "ه",
        "ﺀ": "ء",
        # alif maddah?
        "ﺃ": hamza,
        "ﺄ": hamza,
        "ﺅ": hamza,
        "ﺆ": hamza,
        "ﺇ": hamza,
        "ﺈ": hamza,
        "ﺉ": hamza,
        "ﺊ": hamza,
        "ﺋ": hamza,
        "ﺌ": hamza,
        "ﺍ": alif,
        "ﺎ": alif,
        "ﺏ": "ب",
        "ﺐ": "ب",
        "ﺑ": "ب",
        "ﺒ": "ب",
        "ﺓ": "ة",
        "ﺔ": "ة",
        "ﺕ": "ت",
        "ﺖ": "ت",
        "ﺗ": "ت",
        "ﺘ": "ت",
        "ﺙ": "ث",
        "ﺚ": "ث",
        "ﺛ": "ث",
        "ﺜ": "ث",
        "ﺝ": "ج",
        "ﺞ": "ج",
        "ﺟ": "ج",
        "ﺠ": "ج",
        "ﺡ": "ح",
        "ﺢ": "ح",
        "ﺣ": "ح",
        "ﺤ": "ح",
        "ﺥ": "خ",
        "ﺦ": "خ",
        "ﺧ": "خ",
        "ﺨ": "خ",
        "ﺩ": "د",
        "ﺪ": "د",
        "ﺫ": "ذ",
        "ﺬ": "ذ",
        "ﺭ": "ر",
        "ﺮ": "ر",
        "ﺯ": "ز",
        "ﺰ": "ز",
        "ﺱ": "س",
        "ﺲ": "س",
        "ﺳ": "س",
        "ﺴ": "س",
        "ﺵ": "ش",
        "ﺶ": "ش",
        "ﺷ": "ش",
        "ﺸ": "ش",
        "ﺹ": "ص",
        "ﺺ": "ص",
        "ﺻ": "ص",
        "ﺼ": "ص",
        "ﺽ": "ض",
        "ﺾ": "ض",
        "ﺿ": "ض",
        "ﻀ": "ض",
        "ﻁ": "ط",
        "ﻂ": "ط",
        "ﻃ": "ط",
        "ﻄ": "ط",
        "ﻅ": "ظ",
        "ﻆ": "ظ",
        "ﻇ": "ظ",
        "ﻈ": "ظ",
        "ﻉ": "ع",
        "ﻊ": "ع",
        "ﻋ": "ع",
        "ﻌ": "ع",
        "ﻍ": "غ",
        "ﻎ": "غ",
        "ﻏ": "غ",
        "ﻐ": "غ",
        "ﻑ": "ف",
        "ﻒ": "ف",
        "ﻓ": "ف",
        "ﻔ": "ف",
        "ﻕ": "ق",
        "ﻖ": "ق",
        "ﻗ": "ق",
        "ﻘ": "ق",
        "ﻙ": "ك",
        "ﻚ": "ك",
        "ﻛ": "ك",
        "ﻜ": "ك",
        "ﻝ": "ل",
        "ﻞ": "ل",
        "ﻟ": "ل",
        "ﻠ": "ل",
        "ﻡ": "م",
        "ﻢ": "م",
        "ﻣ": "م",
        "ﻤ": "م",
        "ﻥ": "ن",
        "ﻦ": "ن",
        "ﻧ": "ن",
        "ﻨ": "ن",
        "ﻩ": "ه",
        "ﻪ": "ه",
        "ﻫ": "ه",
        "ﻬ": "ه",
        "ﻭ": "و",
        "ﻮ": "و",
        "ﻯ": "ى",
        "ﻰ": "ى",
        "ﻱ": "ي",
        "ﻲ": "ي",
        "ﻳ": "ي",
        "ﻴ": "ي",
        "ﻵ": "ل" + alif_maddah,
        "ﻶ": "ل" + alif_maddah,
        "ﻷ": "ل" + hamza,
        "ﻸ": "ل" + hamza,
        "ﻹ": "ل" + hamza,
        "ﻺ": "ل" + hamza,
        "ﻻ": "لا",
        "ﻼ": "لا",
    },
    # put shaddah before harakah always
    **{harakah + shaddah: shaddah + harakah for harakah in short_vowels},
}
unicode_cleanup_pattern = compile_map_pattern(unicode_cleanup_map)


def unicode_cleanup(s: str) -> str:
    return sub_map_pattern(unicode_cleanup_pattern, unicode_cleanup_map, s)


subs = {
    alif_maksurah: alif,
    "[\u0622-\u0626-\u0676\u0678]": hamza,
}

diacritic_map = {
    # half_vowel + harakat -> consonant
    **{
        rf"{half_vowel}(?={harakah})": consonant
        for harakah in harakat_wo_shaddah
        for half_vowel, consonant in zip(half_vowels, half_vowels_as_consonants)
    },
    # half_vowel + shaddah -> consonant
    **{
        half_vowel + shaddah: 2 * consonant
        for half_vowel, consonant in zip(half_vowels, half_vowels_as_consonants)
    },
    # short_vowel + half_vowel -> consonant
    **{
        rf"(?<={short_vowel}){half_vowel}": consonant
        for short_vowel in short_vowels
        for half_vowel, consonant in zip(half_vowels, half_vowels_as_consonants)
        if (short_vowel != kasra or half_vowel != ya)
        and (short_vowel != damma or half_vowel != waw)
    },
    # half_vowel at beginning of string -> consonant
    **{
        rf"^{half_vowel}": consonant
        for half_vowel, consonant in zip(half_vowels, half_vowels_as_consonants)
    },
    # TODO: nisba suffix
    fatha + alif: "ā",
    alif: "ā",
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
    **dict(zip(half_vowels, half_vowels_as_vowels)),
}

# if diphthongs
diphthong_map = {
    f"(?<={fatha}){half_vowel}": short_vowel
    for half_vowel, short_vowel in zip(half_vowels, half_vowels_as_short_vowels)
}
diphthong_map = {
    "aw":"au",
    "ay":"ai",
}

# if not double_vowels
double_vowels_map = {
    # uww -> ūw
    "uww": "ūw",
    "iyy": "īy",
}

char_map = {
    "(.)" + shaddah: lambda match: match.group(1) * 2,
    "^" + hamza: "",
    hamza: "ʾ",
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
}

number_map = {
    # numbers
    **{chr(0x660 + i): str(i) for i in range(10)},
    # extended numbers
    **{chr(0x6F0 + i): str(i) for i in range(10)},
    "٪": "%",
    "٫": ",",  # decimal separator
    "٬": ".",  # thousands separator
    "٭": "*",  # 5-pointed star
}
number_map_pattern = compile_single_char_map_pattern(number_map)
number_token_pattern = re.compile(f"[{''.join(number_map)}]+")

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
    "فَ": "fa",
    "و": "wa",
    "وَ": "wa",
}
preposition_prefixes = {
    "ب": "bi",
    "بِ": "bi",
    "ك": "ka",
    "كَ": "ka",
    "ل": "li",
    "لِ": "li",
    # "في": "fi",
    "ل": "li",
    "لِ": "li",
    "ك": "ka",
    "كَ": "ka",
    # "في": "fi",
}
future_prefixes = {
    "س": "sa",
    "سَ": "sa",
}
todo_prefixes = {
    "ت": "ta",
    "تَ": "ta",
    # "": "la",
    # "": "a"
}
article_prefixes = {
    "ال": "al",
    "الْ": "al",
    "أَل": "al",
    "أَلْ": "al",
    # fal, wal, bil, lil
}
conjunction_article_prefixes = {
    con1 + art1: con2 + art2
    for con1, con2 in conjunction_prefixes.items()
    for art1, art2 in article_prefixes.items()
}
prefixes = (
    conjunction_prefixes
    | preposition_prefixes
    | article_prefixes
    | future_prefixes
    | conjunction_article_prefixes
)
prefix_lengths = sorted({len(x) for x in prefixes}, reverse=True)

sentence_stop_marks = ".!?\n"
after_map = {
    "۔": ".",
    "؟": "?",
    "،": ",",
}
after_map_pattern = compile_single_char_map_pattern(after_map)


def sub_after(after):
    return sub_map_pattern(after_map_pattern, after_map, after)
