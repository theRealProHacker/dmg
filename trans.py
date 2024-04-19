import re
from collections import deque
from logging import basicConfig

from pyarabic import araby
from qalsadi import stemnode

import arab_tools
import data
from data import (
    preposition_prefixes,
    sentence_stop_marks,
    token_pattern,
)
from data_types import Case, Profile, Token

try:
    import ner

    ner_available = True
except ImportError as e:
    ner_available = False
    print("NER disabled", e.msg)

basicConfig(level="DEBUG")


def transliterate(text: str, profile: Profile = Profile()) -> str:
    """ """
    # We try to separate the step of gathering information
    # from the step of actually transliterating using that data
    # to increase modularity and seperation of concerns
    text = text.strip()
    text = araby.strip_tatweel(text)
    text = data.unicode_cleanup(text)
    # debug(text)
    if not text:
        return ""
    # tokenization
    matches = [
        (token, match.end(), match.start())
        for match in token_pattern.finditer(text)
        if (token := text[match.start() : match.end()])
    ]
    if not matches:
        return data.sub_after(text)
    tokens, ends, starts = zip(*matches)
    beginning_non_token = data.sub_after(text[: starts[0]])
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
        if any(stop_mark in token.latin_after for stop_mark in sentence_stop_marks):
            sentences.append(current_sentence)
            current_sentence = []
    if current_sentence:
        sentences.append(current_sentence)
    # sentence-level analysis
    names = (
        ner.find_names(
            [
                [araby.strip_diacritics(token.original) for token in sentence]
                for sentence in sentences
            ]
        )
        if ner_available
        else [[False] * len(sentence) for sentence in sentences]
    )
    apply_hamzatul_wasl = deque((False,), 1)
    for sentence, is_name_data in zip(sentences, names):
        sentence[-1].is_end_of_sentence = True
        # word analysis and stemming
        stemmed_words = arab_tools.check_sentence(sentence)
        for token, stemming, is_name in zip(sentence, stemmed_words, is_name_data):
            token.is_name = is_name
            if not stemming:
                print(token.arab, "not found")
                token.lemma = araby.strip_diacritics(token.arab)
                token.pos = "noun"
                prefix_guess = ""
                # TODO: look at the last harakah
                sm = {
                    "marfou3": [],
                    "mansoub": [],
                    "majrour": [],
                    "majzoum": [],
                    "tanwin_marfou3": [],
                    "tanwin_mansoub": [],
                    "tanwin_majrour": [],
                }
            else:
                node = stemnode.StemNode(stemming, True)
                token.lemma, token.pos = node.get_lemma(return_pos=True)
                prefix_guess: str = node.get_affix().split("-")[0]
                sm = node.syntax_mark
            assert token.pos in ("noun", "verb", "stopword", "")
            # print(token.arab, token.lemma, token.pos)

            # applying pausa
            if (token.is_pausa or token.is_end_of_sentence) and token.pos == "noun":
                token.arab = araby.strip_lastharaka(token.arab)

            # prefixes
            if arab_tools.araby.strip_diacritics(token.arab):
                prefix = 0
                for c in prefix_guess:
                    prefix = token.arab.find(c, prefix) + 1
                    if not prefix:
                        break
                if prefix * 2 > len(token.arab):
                    prefix = 0
                while prefix > 0 and token.arab[prefix] in araby.DIACRITICS:
                    prefix += 1
                    if prefix * 2 > len(token.arab):
                        prefix = 0
                if prefix > 0 and (
                    latin_prefix := data.prefixes.get(token.arab[:prefix])
                ):
                    token.prefix = token.arab[:prefix]
                    token.latin_prefix = latin_prefix

            # cases
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
            token.is_definite = len(sm["marfou3"]) + len(sm["mansoub"]) + len(
                sm["majrour"]
            ) > len(sm["tanwin_marfou3"]) + len(sm["tanwin_mansoub"]) + len(
                sm["tanwin_majrour"]
            )

            # hamzatul wasl
            prev_is_hamzatul_wasl = apply_hamzatul_wasl.pop()
            if token.prefix:
                if prev_is_hamzatul_wasl and token.latin_prefix == "al":
                    token.latin_prefix = "l"
            elif len(token.arab) > 2 and (first_letter := token.arab[0]) in (
                data.alif,
                data.alif_wasl,
            ):
                if (short_vowel:=token.arab[1]) in data.short_vowels:
                    token.arab = token.arab[2:]
                    short_vowel = data.diacritic_map[short_vowel]
                elif (
                    first_letter == data.alif
                    and (unvocalized := araby.strip_tashkeel(token.arab[1:]))
                    and (
                        unvocalized in data.hamzatul_wasl_nouns
                        or token.pos == "verb"
                        and any(
                            pattern.fullmatch(unvocalized)
                            for pattern in data.unvocalized_verb_stems_7_to_10
                        )
                    )
                    or first_letter == data.alif_wasl
                ):
                    short_vowel = "i"
                    token.arab = token.arab[1:]
                if not prev_is_hamzatul_wasl:
                    token.hamzatul_wasl_short_vowel = short_vowel

            # applying hamzatul wasl for next token
            apply_hamzatul_wasl.append(
                token.arab[-1] in data.long_vowels
                or token.arab[-1] in data.short_vowels
                or token.arab[-1] == data.alif_maksurah
            )

        # idafah
        for token, next_token in zip(sentence, sentence[1:]):
            token.is_idafah = (
                token.pos == "noun"
                # assimilation not executed yet
                and not token.latin_prefix.endswith("l")
                and token.is_definite
                and next_token.is_genetive
                and next_token.prefix not in preposition_prefixes
            )

    # transliteration
    for token in tokens:
        word = token.arab[len(token.prefix) :]
        # char mapping
        char_map = (
            data.subs | data.special_char_map | data.diacritic_map | data.char_map
        )
        if profile.diphthongs:
            char_map |= data.diphthong_map
        if not profile.double_vowels:
            char_map |= data.double_vowels_map
        if not token.is_idafah:
            char_map = {
                f"(?<=[{data.long_vowels}])ة": "h",
                "ة$": ("h" if profile.ta_marbutah else ""),
            } | char_map
        # if token.is_pausa:
        #     char_map = data.pausa_map | char_map | data.pausa_map
        rules = [(re.compile(arab), latin) for arab, latin in char_map.items()]
        cont: bool = True
        while cont:
            cont = False
            for pattern, replace in rules:
                word, n = pattern.subn(replace, word)
                cont = cont or n
                # if n:
                #     print(word, pattern, replace)
        token.latin = word
        # assimilation
        # sun letter assimilation
        if (
            token.latin_prefix
            and token.latin_prefix[-1] == "l"
            and (first_letter := token.latin[0]) in data.sun_letters
        ):
            token.latin_prefix = token.latin_prefix[:-1] + first_letter
            if len(token.latin) >= 2 and token.latin[1] == first_letter:
                token.latin = token.latin[1:]

    return beginning_non_token + "".join(token.result for token in tokens)


if __name__ == "__main__":
    text = "يَكْتُبُ الكَلْبُ"
    text = "هذا الكتابُ الجديدُ الطالبِ. هو يقرأ الكتابَ الجديدَ."
    # text = "هَذَا الكِتَابُ الْجَدِيدُ الطَالِبِ۔ هُوَ يَقْرَأُ الْكِتَابَ الْجَدِيدَ۔"
    print(transliterate(text))
