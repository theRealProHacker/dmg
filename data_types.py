from dataclasses import dataclass
from typing import Literal

Pos = Literal["stopword", "noun", "verb", ""]

Case = Literal["n", "g", "a", "j", ""]
"""
In arabic: marfoo3,     majroor,        mansoob,        majzoom,        unknown

For nouns: nominative,  genetive,       accusative,     no application, unknown

For verbs: indicative,  no application, subjunctive,    jussive,        unknown
"""

profile_descriptions = {
    # id, title, description, off, on
    "pausa": (
        "Pausa",
        "Ob der Text in Pausa gelesen wird",
        "al-kalbu",
        "al-kalb",
    ),
    "ta_marbutah": (
        "Ta marbuta",
        "Ob die Ta marbuta am Ende eines Wortes wiedergegeben wird",
        "al-madina",
        "al-madinah",
    ),
    "diphthongs": (
        "Diphthonge",
        "Ob Diphthonge ai/au wiedergegeben werden",
        "nawm",
        "naum",
    ),
    "double_vowels": (
        "Geminierte Halbvokale",
        "Ob Halbvokale mit Shaddah als doppelte Konsonanten wiedergegeben werden",
        "nīya",
        "niyya",
    ),
    "nisba": (
        "-ī und -ū",
        "Ob am Ende eines Wortes immer -ī/-ū statt -iyy/-uww wiedergegeben wird",
        "nabiyy o. nabīy, al-ʿarabī",
        "nabī, al-ʿarabī",
    ),
    "begin_hamza": (
        "Anlautendes Hamza",
        "Ob ein anlautendes Hamza wiedergegeben wird",
        "amr",
        "ʾamr",
    ),
    "hu_hi": (
        "-hu und -hi",
        "Ob die Pronomen -hu und -hi ihrer Aussprache entsprechend wiedergegeben werden",
        "baituhu, abūhu",
        "baituhū, abūhu",
    ),
    # for names
    "is_book": (
        "Buchtitel",
        "Ob ein Buchtitel wiedergegeben wird",
        "Kitāb al-Aġānī li-l-Imām Abī l-Faraǧ",
        "Kitāb al-Aġānī li-l-imām abī l-faraǧ",
    ),
    "short_ibn": (
        "b. und bt.",
        "Ob ibn/bin und bint als b. und bt. abgekürzt werden",
        "Muḥammad ibn ʿAbdallāh",
        "Muḥammad b. ʿAbdallāh",
    ),
}


@dataclass
class Profile:
    pausa: bool = False
    ta_marbutah: bool = False
    diphthongs: bool = False
    double_vowels: bool = True
    nisba: bool = True
    begin_hamza: bool = False
    hu_hi: bool = True

    # TODO: imalah, ishmam
    # TODO: Zwei Doppelpunkte bei emphatischen Konsonanten
    # TODO: alif maqsura mit Unterpunkt


@dataclass
class Token:
    def __post_init__(self):
        import data

        self.latin_after = data.sub_after(self.after)
        self.original = self.arab

    arab: str
    after: str = ""
    original: str = ""
    lemma: str = ""
    pos: Pos = ""
    gram_case: Case = ""
    is_definite: bool = False
    prefix: str = ""
    suffix: str = ""
    is_pausa: bool = False
    is_end_of_sentence: bool = False
    is_idafah: bool = False
    is_name: bool = False
    is_nisba: bool = False

    latin: str = ""
    latin_after: str = ""
    latin_prefix: str = ""

    @property
    def is_genetive(self) -> bool:
        return self.pos == "noun" and self.gram_case == "g"

    @property
    def result(self) -> str:
        latin = self.latin
        if self.is_name:
            if len(latin) >= 2 and latin[0] in "ʿʾ" and latin[1] in "aui":
                latin = latin[0] + latin[1:].capitalize()
            else:
                latin = self.latin.capitalize()
        return self.latin_prefix + latin + self.latin_after


Sentence = list[Token]


@dataclass
class NameProfile:
    is_book: bool = False
    short_ibn: bool = True
    ta_marbutah: bool = False
    diphthongs: bool = False
    double_vowels: bool = True
    begin_hamza: bool = False
    hu_hi: bool = True
    nisba: bool = True
