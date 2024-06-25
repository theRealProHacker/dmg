"""
The data module encapsulates all static data to represent a single source of truth
for all other modules
"""

import json
import re
from collections import defaultdict
from contextlib import contextmanager

from pyarabic import araby

from data_types import Case


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write(path, to_save, indent: int = 2):
    with open(path, "w", encoding="utf-8") as f:
        return json.dump(to_save, f, ensure_ascii=False, indent=indent)


@contextmanager
def readWrite(path):
    data = read(path)
    try:
        yield data
    finally:
        write(path, data)


known_names: set[str] = {
    *read("data/ner.json"),
    "محمد",
    "القاهرة",
    # ibrahim 2x
    "إبرهيم",
    "إبراهيم",
    # yasin
    "ياسين",
    # 3amr
    "عمرو",
}


freq_dict = {}
unknown_dict = {}

for entry in read("data/wordfreq.json"):
    freq_dict[(entry["vocalized"], entry["word_type"])] = entry["freq"]
    freq_dict[(entry["unvocalized"], entry["word_type"])] = entry["freq"]
    unknown_dict[entry["unvocalized"]] = entry

noun_dict: dict[str, list] = defaultdict(list)

for entry in read("./data/nouns.json"):
    noun_dict[entry["normalized"]].append(entry)

verb_dict: dict[str, list] = defaultdict(list)

for entry in read("./data/verbs.json"):
    verb_dict[entry["stamped"]].append(entry)

# stopword_dict: dict[str, list] = defaultdict(list)

# for entry in read("./data/stopwords.json"):
#     stopword_dict[(entry["vocalized"], entry["word_type"])] = entry
#     stopword_dict[(entry["unvocalized"], entry["word_type"])] = entry

stopword_dict: dict[str, list] = defaultdict(list)

for entry in read("./data/cstopwords.json"):
    stopword_dict[entry["WORD"]].append(entry)

sem_derivations: dict[str, tuple[str, str]] = {}

for entry in read("./data/semantic_derivations.json"):
    sem_derivations.setdefault(entry["derived"], (entry["verb"], entry["type"]))


sem_relations: dict[tuple[str, str], str] = {}

for entry in read("./data/semantic_relations.json"):
    sem_relations.setdefault((entry["first"], entry["second"]), entry["rule"])


def compile_single_char_map_pattern(d: dict[str, str]) -> re.Pattern:
    return re.compile(f"[{''.join(d)}]")


def compile_map_pattern(d: dict[str, str]) -> re.Pattern:
    return re.compile("|".join(re.escape(x) for x in d))


def sub_map_pattern(pattern, d: dict[str, str], s: str) -> str:
    return pattern.sub(lambda x: d[x.group()], s)


alif = "\u0627"
waw = "\u0648"
alif_maksurah = "\u0649"
ya = "\u064a"
fathatan = "\u064b"
dammatan = "\u064c"
kasratan = "\u064d"
fatha = "\u064e"
damma = "\u064f"
kasra = "\u0650"
shaddah = "\u0651"
sukun = "\u0652"
hamza = "\u0621"
alif_maddah = "\u0622"
alif_wasl = "ٱ"

short_vowels = fatha + damma + kasra
tanween = fathatan + dammatan + kasratan
harakat_wo_shaddah = short_vowels + tanween + sukun
harakat = harakat_wo_shaddah + shaddah
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
        # small alif
        "\u0670": alif,
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
        "ﺁ": alif_maddah,
        "ﻵ": "ل" + alif_maddah,
        "ﻶ": "ل" + alif_maddah,
        "ﻷ": "ل" + hamza,
        "ﻸ": "ل" + hamza,
        "ﻹ": "ل" + hamza,
        "ﻺ": "ل" + hamza,
        "ﻻ": "لا",
        "ﻼ": "لا",
        "ﷲ": "الله",
    },
    # put shaddah before harakah always
    **{harakah + shaddah: shaddah + harakah for harakah in harakat_wo_shaddah},
    # put fathatan before alif always (to protect it from pausa)
    alif + fathatan: fathatan + alif,
    alif_maddah + fathatan: fathatan + alif_maddah,
    # remove left to right marker
    "\u200e": "",
    # replace alif wasl with alif because they are treated the same
    # assumes alif wasl only appears at the beginning of a word
    alif_wasl: alif,
}
unicode_cleanup_pattern = compile_map_pattern(unicode_cleanup_map)


def unicode_cleanup(s: str) -> str:
    return sub_map_pattern(unicode_cleanup_pattern, unicode_cleanup_map, s)


subs = {
    "[\u0623-\u0626-\u0676\u0678]": hamza,
}

vowel_map = {
    # half_vowel at beginning of string -> consonant
    **{
        rf"^{half_vowel}": consonant
        for half_vowel, consonant in zip(half_vowels, half_vowels_as_consonants)
    },
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
    # other short_vowel + half_vowel -> consonant
    **{
        rf"(?<={short_vowel}){half_vowel}": consonant
        for short_vowel in short_vowels
        for half_vowel, consonant in zip(half_vowels, half_vowels_as_consonants)
        if (short_vowel != kasra or half_vowel != ya)
        and (short_vowel != damma or half_vowel != waw)
    },
    # alif + half_vowel -> consonant
    **{
        rf"(?<={alif}){half_vowel}": consonant
        for half_vowel, consonant in zip(half_vowels, half_vowels_as_consonants)
    },
    # alif variants
    alif_maddah: hamza + alif,
    alif_maksurah: alif,
    # harakat + long vowel
    fathatan + alif + "$": "an",
    fatha + alif: "ā",
    damma + waw: "ū",
    kasra + ya: "ī",
    # long vowels alone
    waw + alif: waw,
    alif: "ā",
    **dict(zip(half_vowels, half_vowels_as_vowels)),
    # harakat
    fatha: "a",
    damma: "u",
    kasra: "i",
    fathatan: "an",
    dammatan: "un",
    kasratan: "in",
    sukun: "",
    # ...
    "ūā$": "ū",
}


def half_vowel_is_long(word: str, i: int):
    assert word[i] in half_vowels
    if i == 0:
        return False
    if len(word) > i + 1:
        if word[i - 1] == alif:
            return False
        for haraka in harakat:
            if word[i + 1] == haraka:
                return False
        for short_vowel in short_vowels:
            if (
                word[i - 1] == short_vowel
                and (short_vowel != kasra or word[i] != ya)
                and (short_vowel != damma or word[i] != waw)
            ):
                return False
    return True


# if diphthongs
diphthong_map = {
    f"(?<={fatha}){half_vowel}": short_vowel
    for half_vowel, short_vowel in zip(half_vowels, half_vowels_as_short_vowels)
}
diphthong_map = {
    f"(?<=[aā]){l_hw}(?!a|u|i)": short_vowel
    for l_hw, short_vowel in zip(half_vowels_as_consonants, half_vowels_as_short_vowels)
}

# if not double_vowels
double_vowels_map = {
    # uww -> ūw
    "uww": "ūw",
    "iyy": "īy",
}

# if nisba
nisba_map = {
    "iyy$": "ī",
    "īy$": "ī",
}

# if not begin_hamza
begin_hamza_map = {"^" + hamza + "(?!$)": ""}

con_map = {
    "(.)" + shaddah: lambda match: match.group(1) * 2,
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

# Not currently necessary
# pausa_map = {
#     "[" + fatha + damma + kasra + fathatan + dammatan + kasratan + shaddah + "]$": "",
#     fathatan + alif + "$": alif,
#     alif + fathatan + "$": alif,
# }

sun_letters = {"ت", "ث", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ن"}

# latin sun letters
sun_letters = set("tṯdḏrzsšṣḍṭẓn")

# Pattern to match an arabic word
token_pattern = re.compile(f"[\u0621-\u0655{alif_wasl}]+")


sentence_stop_marks = ".!?\n"
after_map = {
    "۔": ".",
    "؟": "?",
    "،": ",",
}
after_map_pattern = compile_single_char_map_pattern(after_map)


def sub_after(after):
    return sub_map_pattern(after_map_pattern, after_map, after)


# hamzatul wasl
# Without the starting alif
hamzatul_wasl_nouns = {
    # ithnan
    "ثنان",
    "ثنين",
    "ثنتان",
    "ثنتين",
    # ibn
    "بن",
    # ism
    "سم",
    # imra'a
    "مرأ",
    # imra'at
    "مرأة",
    "مرأت",
}

# consonant pattern
_cp = f"([{araby.LETTERS[1:]}])"
unvocalized_verb_stems_7_to_10_verbs = {
    # 7
    f"ن{_cp}{_cp}{_cp}",
    # 8
    f"{_cp}ت{_cp}{_cp}",
    # 9
    f"{_cp}{_cp}{_cp}{shaddah}?",
    # 10
    f"ست{_cp}{_cp}{_cp}",
}

unvocalized_verb_stems_7_to_10_nouns = {
    # 7
    f"ن{_cp}{_cp}{alif}{_cp}",
    # 8
    f"{_cp}ت{_cp}{alif}{_cp}",
    # 9
    f"{_cp}{_cp}{alif}{_cp}",
    # 10
    f"ست{_cp}{_cp}{alif}{_cp}",
}

unvocalized_verb_stems_7_to_10 = [
    re.compile(p)
    for p in unvocalized_verb_stems_7_to_10_verbs | unvocalized_verb_stems_7_to_10_nouns
]

# case + definiteness
case_mapping: dict[str, tuple["Case", bool]] = {
    fatha: ("a", True),
    damma: ("n", True),
    kasra: ("g", True),
    fathatan: ("a", False),
    dammatan: ("n", False),
    kasratan: ("g", False),
}

special_words = {
    # ma3a
    "مع",
    # (all pronouns)
    "أنا",
    "أنت",
    "أنتم",
    "أنتن",
    "هو",
    "هي",
    "هم",
    "هن",
    "نحن",
}

add_alif_words = {
    # ilah
    "إِلَه": 2,
    # rahman
    "رَحْمَن": 3,
    # hadha
    "هَذَا": 1,
    "هَذِهِ": 1,
    # dhalika
    "ذَلِكَ": 1,
    "كَذَلِكَ": 2,
    # hakadha
    "هَكَذَا": 1,
    # lakin
    "لَكِنْ": 1,
    "لَكِنَّ": 1,
    # taha
    "طَهَ": (1, 3),  # 3 after the first has been inserted
}
