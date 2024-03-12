from dataclasses import dataclass
from typing import Literal

import data

Pos = Literal["stopword", "noun", "verb", ""]

Case = Literal["n", "g", "a", "j", ""]
"""
In arabic: marfoo3,     majroor,        mansoob,        majzoom,        unknown

For nouns: nominative,  genetive,       accusative,     no application, unknown

For verbs: indicative,  no application, subjunctive,    jussive,        unknown
"""


@dataclass
class Profile:
    pausa: bool = False
    ta_marbutah: bool = False
    diphthongs: bool = False
    double_vowels: bool = True
    # skip_i3rab: bool = False
    # """Whether i3rab (flexion endings) should be skipped"""
    # full_vocalisation: bool = False
    # """ Full vocalised transcription"""
    # TODO: imalah, ishmam
    # TODO: alif maqsura to ya
    # TODO: Zwei Doppelpunkte bei emphatischen Konsonanten
    # TODO: alif maqsura mit Unterpunkt
    # IDEA: Whether to use ner
    # IDEA: Capitalize beginning of each sentence

    descriptions = {
        "pausa": (
            "Pausa",
            "Ob der Text in Pausa gelesen werden soll",
        ),
        "ta_marbutah": (
            "Ta marbuta",
            "Ob die Ta marbuta am Ende eines Wortes wiedergegeben werden soll",
        ),
        "diphthongs": (
            "Diphthonge",
            "Ob Diphthonge wiedergegeben werden sollen",
        ),
        "double_vowels": (
            "Doppelte Halbvokale",
            "Ob Halbvokale mit Shaddah als verdoppelte Konsonanten wiedergegeben werden sollen",
        ),
    }


@dataclass
class Token:
    def __post_init__(self):
        self.latin_after = data.sub_after(self.after)

    arab: str
    after: str = ""
    lemma: str = ""
    pos: Pos = ""
    gram_case: Case = ""
    prefix: str = ""
    is_pausa: bool = False
    is_end_of_sentence: bool = False
    is_idafah: bool = False
    is_name: bool = False
    apply_hamzatul_wasl: bool = False

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
            if len(latin) >= 2 and latin[0] == "ʿ" and latin[1] in "aui":
                latin = "ʿ" + latin[1:].capitalize()
            else:
                latin = self.latin.capitalize()
        return (
            (self.latin_prefix + "-" if self.prefix else "") + latin + self.latin_after
        )

    @property
    def original(self) -> str:
        # This is not true for a short amount of time after the prefix is set, but has not yet been deducted from arab
        return self.prefix + self.arab + self.after


Sentence = list[Token]
