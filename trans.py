import re
from dataclasses import dataclass
from typing import Literal

from pyarabic import araby
from qalsadi import stemnode

import data
from arab_tools import Analex
from data import (
    after_map,
    after_map_pattern,
    article_prefixes,
    preposition_prefixes,
    sentence_stop_marks,
    sub_map_pattern,
    token_pattern,
)

analex = Analex()

Pos = Literal["s", "n", "v", ""]
"""
stopword, noun, verb, punctuation
"""
Case = Literal["n", "g", "a", "j", ""]
"""
In arabic: marfoo3,     majroor,        mansoob,        majzoom,        unknown

For nouns: nominative,  genetive,       accusative,     no application, unknown

For verbs: indicative,  no application, subjunctive,    jussive,        unknown
"""


@dataclass
class Profile:
    pausa: bool = False
    ta_marbatuh: bool = False
    # skip_i3rab: bool = False
    # """Whether i3rab (flexion endings) should be skipped"""
    # full_vocalisation: bool = False
    # """ Full vocalised transcription"""
    # TODO: Diphtonge: aw -> au
    # TODO: niyyah -> nīyah, awwal -> auwal
    # TODO: imalah, ishmam
    # TODO: alif maqsura to ya
    # TODO: Zwei Doppelpunkte bei emphatischen Konsonanten
    # TODO: alif maqsura mit Unterpunkt

    descriptions = {
        "pausa": (
            "Pausa",
            "Ob der Text in Pausa gelesen werden soll",
        ),
        "ta_marbatuh": (
            "Ta marbuta",
            "Ob die Ta marbuta am Ende eines Wortes wiedergegeben werden soll",
        ),
    }


@dataclass
class Token:
    def __post_init__(self):
        self.latin_after = sub_map_pattern(after_map_pattern, after_map, self.after)

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

    latin: str = ""
    latin_after: str = ""
    latin_prefix: str = ""

    @property
    def is_genetive(self) -> bool:
        return self.pos == "n" and self.gram_case == "g"

    @property
    def result(self) -> str:
        if self.is_name:
            self.latin = self.latin.capitalize()
        return (
            (self.latin_prefix + "-" if self.prefix else "")
            + self.latin
            + self.latin_after
        )


def transliterate(text: str, profile: Profile = Profile()) -> str:
    """ """
    # We try to separate the step of gathering information
    # from the step of actually transliterating using that data
    # to increase modularity and seperation of concerns
    text = text.strip()
    if not text:
        return ""
    # tokenization
    tokens, ends, starts = zip(
        *(
            (token, match.end(), match.start())
            for match in token_pattern.finditer(text)
            if (token := text[match.start() : match.end()])
        )
    )
    if not tokens:
        return ""
    starts = [*starts[1:], len(text)]
    tokens = [
        Token(token, after=text[end:start], is_pausa=profile.pausa)
        for token, end, start in zip(tokens, ends, starts)
    ]
    # sentence splitting
    sentences: list[list[Token]] = []
    current_sentence: list[Token] = []
    for token in tokens:
        current_sentence.append(token)
        if any(stop_mark in token.after for stop_mark in sentence_stop_marks):
            token.is_end_of_sentence = True
            sentences.append(current_sentence)
            current_sentence = []
    if current_sentence:
        sentences.append(current_sentence)

    for sentence in sentences:
        # word analysis and stemming
        stemmed_words = analex.check_words([token.arab for token in sentence])
        for token, stemming in zip(sentence, stemmed_words):
            if not stemming:
                continue
            node = stemnode.StemNode(stemming, True)
            token.lemma, token.pos = node.get_lemma(return_pos=True)
            # print(token.arab, token.lemma, token.pos)
            prefix: str = node.get_affix().split("-")[0]
            max_prefix_length = len(prefix)
            for prefix_length in data.prefix_lengths:
                if (
                    prefix_length <= max_prefix_length
                    and token.arab.startswith(possible_prefix := prefix[:prefix_length])
                    and (latin_prefix := data.prefixes.get(possible_prefix))
                ):
                    token.prefix = possible_prefix
                    token.latin_prefix = latin_prefix
                    break
            sm = node.syntax_mark
            cases: dict[Case, int] = {
                "n": len(sm["marfou3"]) + len(sm["tanwin_marfou3"]),
                "a": len(sm["mansoub"]) + len(sm["tanwin_mansoub"]),
                "g": len(sm["majrour"]) + len(sm["tanwin_majrour"]),
                "j": len(sm["majzoum"]),
            }
            sorted_cases = sorted(cases, key=cases.get, reverse=True)
            token.gram_case = (
                ""
                if cases[sorted_cases[0]] == cases[sorted_cases[1]]
                else sorted_cases[0]
            )
        # idafah
        for token, next_token in zip(sentence, sentence[1:]):
            token.is_idafah = (
                token.pos == "n"
                and next_token.is_genetive
                and next_token.prefix not in preposition_prefixes
            )

    # transliteration
    for token in tokens:
        word = token.arab[len(token.prefix) :]
        if token.is_pausa:
            word = araby.strip_lastharaka(word)
        # char mapping
        char_map = (
            data.subs | data.diacritic_map | data.char_map | data.special_char_map
        )
        # if token.is_pausa:
        #     char_map = data.pausa_map | char_map | data.pausa_map
        rules = [(re.compile(arab), latin) for arab, latin in char_map.items()]
        cont: bool = True
        while cont:
            cont = False
            for pattern, replace in rules:
                word, n = pattern.subn(replace, word)
                if n:
                    cont = True
        token.latin = word
        # assimilation
        # sun letter assimilation
        if (
            token.prefix in article_prefixes
            and (first_letter := token.latin[0]) in data.sun_letters
        ):
            token.latin_prefix = token.latin_prefix[:-1] + first_letter

    return "".join(token.result for token in tokens)


if __name__ == "__main__":
    text = "يَكْتُبُ الكَلْبُ"
    text = "هذا الكتابُ الجديدُ الطالبِ. هو يقرأ الكتابَ الجديدَ."
    text = "هَذَا الكِتَابُ الْجَدِيدُ الطَالِبِ۔ هُوَ يَقْرَأُ الْكِتَابَ الْجَدِيدَ۔"
    print(transliterate(text))
