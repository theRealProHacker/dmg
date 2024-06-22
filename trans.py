import re
from collections import deque

from pyarabic import araby

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


def transliterate(text: str, profile: Profile = Profile()) -> str:
    """ """
    # We try to separate the step of gathering information
    # from the step of actually transliterating using that data
    # to increase modularity and seperation of concerns
    text = text.strip()
    text = araby.strip_tatweel(text)
    text = data.unicode_cleanup(text)
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

    tokens = [
        Token(token, after=text[end:start], is_pausa=profile.pausa)
        for token, end, start in zip(tokens, ends, [*starts[1:], len(text)])
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
    apply_hamzatul_wasl = False
    next_wasl: str = ""
    for sentence, is_name_data in zip(sentences, names):
        sentence[-1].is_end_of_sentence = True
        # word analysis and stemming
        stemmed_words = [*arab_tools.check_sentence(sentence)]
        for token, stemming, is_name in zip(sentence, stemmed_words, is_name_data):
            token.is_name, token.lemma, token.pos, prefix_guess, sm = is_name, *stemming
            assert token.pos in ("noun", "verb", "stopword", "")
            # applying pausa
            if token.is_pausa and token.pos == "noun":
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
            prev_ended_vowel = apply_hamzatul_wasl

            # applying hamzatul wasl for next token
            arab = token.arab
            apply_hamzatul_wasl = (
                arab[-1] in (data.alif, data.alif_maksurah)
                and (len(arab) == 1 or arab[-2] != data.fathatan)
                or arab[-1] in data.half_vowels
                and data.half_vowel_is_long(arab, len(arab) - 1)
                or arab[-1] in data.short_vowels
            )
            next_wasl = (
                "u"
                if arab_tools.hum_pattern(arab) or arab_tools.antum_pattern(arab)
                else ""
            )

            if len(araby.strip_diacritics(arab)) <= 2:
                continue

            if token.prefix:
                if prev_ended_vowel and token.latin_prefix == "al":
                    token.latin_prefix = "l"
                # every other prefix ends on a short vowel
                prev_ended_vowel = not token.latin.endswith("l")
            elif token.arab[0] in (
                data.alif,
                data.alif_wasl,
            ):
                token.arab = token.arab[1:]
                haraka = token.arab[0] in data.short_vowels
                if prev_ended_vowel:
                    if haraka:
                        token.arab = token.arab[1:]
                elif not haraka:
                    if token.arab[0] == "ل":
                        haraka = "a"
                    elif araby.separate(token.arab)[1][1] == data.damma:
                        haraka = "u"
                    else:
                        haraka = "i"
                    token.arab = (next_wasl or haraka) + token.arab

        # idafah
        for token, next_token in zip(sentence, sentence[1:]):
            token.is_idafah = (
                token.pos == "noun"
                # sun letter assimilation not executed yet
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
            data.subs
            | data.special_char_map
            | data.vowel_map
            | (
                {
                    f"(?<=[āūī])ة$": "h",
                    "ة$": ("h" if profile.ta_marbutah else ""),
                }
                if not token.is_idafah
                else {}
            )
            | (data.begin_hamza_map if not profile.begin_hamza else {})
            | data.con_map
        )
        if profile.diphthongs:
            char_map |= data.diphthong_map
        if not profile.double_vowels:
            char_map |= data.double_vowels_map
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
