import re
from contextlib import suppress

from pyarabic import araby

import arab_tools
import data
from data import (
    sentence_stop_marks,
    token_pattern,
)
from data_types import Profile, Token

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
    # NER
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
            (
                token.is_name,
                token.lemma,
                token.pos,
                token.gram_case,
                token.is_definite,
                prefix_suggestion,
                token.suffix,
            ) = is_name, *stemming
            assert token.pos in ("noun", "verb", "stopword", "")

            # applying pausa
            if (
                token.is_pausa
                and token.pos == "noun"
                and not token.gram_case == "a"
                and not token.suffix
            ):
                token.arab = araby.strip_lastharaka(token.arab)

            # getting the prefix
            rasm, harakat = arab_tools.separate(token.arab)
            sug_rasm, sug_harakat = arab_tools.separate(prefix_suggestion)
            i = 0  # the index in the rasm

            def get_rasm(i: int) -> bool:
                return sug_rasm[i] if sug_rasm[i] == rasm[i] else "___"

            def check_haraka(i: int, haraka: str) -> bool:
                return (not harakat[i] or harakat[i] == haraka) and (
                    not sug_harakat[i] or sug_harakat[i] == haraka
                )

            with suppress(IndexError):
                # wa- and fa- prefix
                if (conjunction := get_rasm(i)) in "فو" and check_haraka(i, data.fatha):
                    token.latin_prefix += ("w" if conjunction == "و" else "f") + "a-"
                    i += 1
                # sa- prefix
                next_letter = get_rasm(i)
                if next_letter == "س" and check_haraka(i, data.fatha):
                    token.latin_prefix += "sa-"
                    i += 1
                # li-, bi-, ka- and then al- prefix
                elif next_letter in "لباك":
                    if next_letter in "لب" and (
                        not harakat[i] or harakat[i] == data.kasra
                    ):
                        token.latin_prefix += (
                            "l" if next_letter == "ل" else "b"
                        ) + "i-"
                        i += 1
                        if (
                            next_letter == "ل"
                            and rasm[i] == "ل"
                            and (not harakat[i] or harakat[i] == data.sukun)
                        ):
                            token.latin_prefix += "l-"
                            i += 1
                    elif next_letter == "ك" and (
                        not harakat[i] or harakat[i] == data.fatha
                    ):
                        token.latin_prefix += "ka-"
                        i += 1
                if (
                    get_rasm(i) == "ا"
                    and check_haraka(i, "")
                    and get_rasm(i + 1) == "ل"
                    and check_haraka(i + 1, data.sukun)
                ):
                    token.latin_prefix += "al-" if not i else "l-"
                    i += 2
            token.prefix = arab_tools.join(rasm[:i], harakat[:i])
            token.arab = arab_tools.join(rasm[i:], harakat[i:])

            # special cases
            if arab_tools.allah_pattern(token.arab):
                token.arab = arab_tools.inject("ا", token.arab, 3)
                token.is_name = not apply_hamzatul_wasl
            elif arab_tools.lillah_pattern(token.arab):
                token.prefix = "لِ"
                token.latin_prefix = "li-"
                token.arab = "للاهِ" if not token.is_pausa else "للاه"

            if (
                profile.hu_hi
                and araby.strip_harakat(token.suffix) == "ه"
                and (haraka := token.arab[-1]) in (data.damma, data.kasra)
                and len(token.arab) >= 3
                and rasm[-2] not in data.half_vowels
            ):
                token.arab += data.waw if haraka == data.damma else data.ya

            # hamzatul wasl
            # applying hamzatul wasl for next token
            arab = token.arab
            prev_ended_vowel = apply_hamzatul_wasl
            prev_wasl = next_wasl
            apply_hamzatul_wasl = (
                arab[-1] in (data.alif, data.alif_maksurah)
                and (len(arab) == 1 or arab[-2] != data.fathatan)
                or arab[-1] in data.half_vowels
                and data.half_vowel_is_long(arab, len(arab) - 1)
                or arab[-1] in data.short_vowels
            )  # TODO: and no number between
            next_wasl = (
                "u"
                if arab_tools.hum_pattern(arab) or arab_tools.antum_pattern(arab)
                else ""
            )

            if len(araby.strip_diacritics(arab)) <= 2:
                continue

            if token.prefix:
                if prev_ended_vowel and token.latin_prefix == "al-":
                    token.latin_prefix = "l-"
                elif token.latin_prefix == "al-" and prev_wasl:
                    token.latin_prefix = prev_wasl + "l-"
                # every other prefix ends on a short vowel
                prev_ended_vowel = not token.latin_prefix.endswith("l-")
            if token.arab[0] in (
                data.alif,
                data.alif_wasl,
            ):
                token.arab = token.arab[1:]
                haraka = token.arab[0] in data.short_vowels
                if prev_ended_vowel:
                    if haraka:
                        token.arab = token.arab[1:]
                elif not haraka:
                    if token.arab[0] == "ل":  # and not matches something else
                        haraka = "a"
                    elif araby.separate(token.arab)[1][1] == data.damma:
                        haraka = "u"
                    else:
                        haraka = "i"
                    token.arab = (prev_wasl or haraka) + token.arab

        # idafah
        for token, next_token in zip(sentence, sentence[1:]):
            token.is_idafah = (
                token.pos == "noun"
                # sun letter assimilation not executed yet
                and not token.latin_prefix.endswith("l-")
                and token.is_definite
                and not token.suffix
                and token.after.isspace()  # there can't be anything else (like numbers, etc.) between
                and next_token.is_genetive
                and next_token.latin_prefix in ("al-", "l-", "")
            )

    # transliteration
    for token in tokens:
        word = token.arab
        # char mapping
        char_map = (
            data.subs
            | data.vowel_map
            | (
                {
                    "(?<=[āūī])ة$": "h",
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
        if profile.nisba:
            char_map |= data.nisba_map
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
        # sun letter assimilation
        prefix = token.latin_prefix
        if (
            prefix
            and prefix[-2] == "l"
            and (first_letter := word[0]) in data.sun_letters
        ):
            token.latin_prefix = prefix[:-2] + first_letter + "-"
            if len(word) >= 2 and word[1] == first_letter:
                word = word[1:]
        token.latin = word

    return beginning_non_token + "".join(token.result for token in tokens)


if __name__ == "__main__":
    text = "يَكْتُبُ الكَلْبُ"
    text = "هذا الكتابُ الجديدُ الطالبِ. هو يقرأ الكتابَ الجديدَ."
    text = "هَذَا الكِتَابُ الْجَدِيدُ الطَالِبِ۔ هُوَ يَقْرَأُ الْكِتَابَ الْجَدِيدَ۔"
    print(transliterate(text))
