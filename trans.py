import re
from logging import basicConfig, debug

from pyarabic import araby
from qalsadi import stemnode

import arab_tools
import data
from data import (
    article_prefixes,
    preposition_prefixes,
    sentence_stop_marks,
    token_pattern,
)
from data_types import Case, Profile, Token

try:
    import ner

    ner_available = True
except ImportError:
    ner_available = False

basicConfig(level="DEBUG")


def transliterate(text: str, profile: Profile = Profile()) -> str:
    """ """
    # We try to separate the step of gathering information
    # from the step of actually transliterating using that data
    # to increase modularity and seperation of concerns
    text = text.strip()
    text = araby.strip_tatweel(text)
    text = data.unicode_cleanup(text)
    debug(text)
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
    for sentence, is_name_data in zip(sentences, names):
        sentence[-1].is_end_of_sentence = True
        # named entity recognition
        for token, is_name in zip(sentence, is_name_data):
            token.is_name = is_name
        # word analysis and stemming
        stemmed_words = arab_tools.check_sentence(sentence)
        for token, stemming in zip(sentence, stemmed_words):
            if not stemming:
                continue
            node = stemnode.StemNode(stemming, True)
            token.lemma, token.pos = node.get_lemma(return_pos=True)
            assert token.pos in ("noun", "verb", "stopword", "")
            # print(token.arab, token.lemma, token.pos)
            # prefixes
            if not token.prefix:
                prefix_guess: str = node.get_affix().split("-")[0]
                possible_prefixes = arab_tools.possible_prefixes(
                    token.arab, prefix_guess
                )
                if possible_prefixes:
                    token.prefix = possible_prefixes[0]
                    token.latin_prefix = data.prefixes[token.prefix]
            # cases
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
            # hamzatul wasl for token
            if token.latin_prefix and token.latin_prefix[-1] not in ("a", "i"):
                # we don't care about hamzatul wasl
                continue
            first_char = token.arab[0]
            if first_char == data.alif_wasl or first_char == data.alif:
                token.apply_hamzatul_wasl = True
                token.arab = data.hamza + token.arab[1:]
            elif first_char == data.hamza:
                token.apply_hamzatul_wasl = arab_tools.is_hamzatul_wasl(token)
        # two tokens together
        for token, next_token in zip(sentence, sentence[1:]):
            # idafah
            # TODO: first token has no article but is definite
            token.is_idafah = (
                token.pos == "noun"
                and next_token.is_genetive
                and next_token.prefix not in preposition_prefixes
            )
            # hamzatul_wasl
            if next_token.prefix:
                if next_token.prefix in article_prefixes:
                    next_token.latin_prefix = "l"
                continue
            # don't apply hamzatul wasl if previous token doesn't end with a vowel
            if token.is_pausa:
                next_token.apply_hamzatul_wasl = False
            elif not (
                token.arab[-1] in data.long_vowels
                or token.arab[-1] in data.short_vowels
            ):
                next_token.apply_hamzatul_wasl = False

    # transliteration
    for token in tokens:
        word = token.arab[len(token.prefix) :]
        if token.is_pausa or token.is_end_of_sentence:
            word = araby.strip_lastharaka(word)
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
        if token.apply_hamzatul_wasl:
            char_map |= data.hamzatul_wasl_map
        # if token.is_pausa:
        #     char_map = data.pausa_map | char_map | data.pausa_map
        rules = [(re.compile(arab), latin) for arab, latin in char_map.items()]
        cont: bool = True
        while cont:
            cont = False
            for pattern, replace in rules:
                word, n = pattern.subn(replace, word)
                cont = cont or n
                if n:
                    print(word, pattern, replace)
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
