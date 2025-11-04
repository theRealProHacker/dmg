import os
import re
from contextlib import suppress

from pyarabic import araby

import arab_tools
import data
from arab_tools import gen_arab_pattern_match
from data import (
    sentence_stop_marks,
    token_pattern,
)
from data_types import IJMESProfile, NameProfile, Profile, Token

hum_pattern = gen_arab_pattern_match("هُمْ")
antum_pattern = gen_arab_pattern_match("أَنْتُمْ")
min_pattern = gen_arab_pattern_match("مِنْ")

allah_pattern = gen_arab_pattern_match("الله")
lillah_pattern = gen_arab_pattern_match("لله")
ulaika_pattern1 = gen_arab_pattern_match("أُولَئِكَ")
ulaika_pattern2 = gen_arab_pattern_match("أُولَائِكَ")
ana_pattern = gen_arab_pattern_match("أَنَا")
amru_pattern = gen_arab_pattern_match("عَمْرو")

add_alif_patterns = [
    (gen_arab_pattern_match(k), (v,) if isinstance(v, int) else v)
    for k, v in data.add_alif_words.items()
]


# name specific
abd_pattern = gen_arab_pattern_match("عَبْد")
processed_allah_pattern = gen_arab_pattern_match("aللاه")
ibn_pattern = gen_arab_pattern_match("ابْن")
bin_pattern = gen_arab_pattern_match("بِنْ")
bint_pattern = gen_arab_pattern_match("بِنْت")
kitab_pattern = gen_arab_pattern_match("كتاب")


def transliterate(text: str, profile: Profile | NameProfile = Profile()) -> str:
    """ """
    profile_is_name = isinstance(profile, NameProfile)
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
        Token(token, after=text[end:start], is_pausa=profile_is_name or profile.pausa) # type: ignore
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

    apply_hamzatul_wasl = False
    next_wasl: str = ""
    for sentence in sentences:
        sentence[-1].is_end_of_sentence = True

        # names specific:
        # capitalize first word of book title
        # and the second if the first is "kitab"
        if profile_is_name and profile.is_book:
            sentence[0].is_name = True
            if len(sentence) > 1 and kitab_pattern(tokens[0].arab):
                tokens[1].is_name = True

        # word analysis and stemming
        stemmed_words = [*arab_tools.check_sentence(sentence)]
        for token_i, (token, stemming) in enumerate(zip(sentence, stemmed_words)):
            (
                token.lemma,
                token.pos,
                token.gram_case,
                token.is_definite,
                prefix_suggestion,
                verb_ending,
                token.suffix,
                _,
            ) = stemming
            if profile_is_name and not profile.is_book:
                token.is_name = True
            assert token.pos in ("noun", "verb", "stopword", "")

            # applying pausa
            if (
                token.is_pausa
                and token.pos == "noun"
                and not (token.gram_case == "a" and not token.is_definite)
                and not token.suffix
            ):
                token.arab = araby.strip_lastharaka(token.arab)

            # getting the prefix
            rasm, harakat = arab_tools.separate(token.arab)
            sug_rasm, sug_harakat = arab_tools.separate(prefix_suggestion)
            i = 0  # the index in the rasm

            def get_rasm(i: int) -> str:
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
                elif next_letter in "لبك":
                    if next_letter in "لب" and check_haraka(i, data.kasra):
                        token.latin_prefix += (
                            "l" if next_letter == "ل" else "b"
                        ) + "i-"
                        i += 1
                        if (
                            next_letter == "ل"
                            and rasm[i] == "ل"
                            and check_haraka(i, data.sukun)
                        ):
                            token.latin_prefix += "l-"
                            i += 1
                    elif next_letter == "ك" and check_haraka(i, data.fatha):
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

            # with suppress(IndexError):
            #     def check_haraka(i: int, haraka: str) -> bool:
            #         return (not harakat[i] or harakat[i] == haraka)

            #     if (
            #         not token.latin_prefix.endswith("l-")
            #         and rasm[i] == "ا"
            #         and token.pos == "noun"
            #         and token.is_definite
            #         and check_haraka(i, "")
            #         and rasm[i + 1] == "ل"
            #         and check_haraka(i + 1, data.sukun)
            #         and data.shaddah in harakat[i + 2]
            #     ):
            #         token.latin_prefix += "al-" if not i else "l-"
            #         i += 2

            token.prefix = arab_tools.join(rasm[:i], harakat[:i])
            token.arab = arab_tools.join(rasm[i:], harakat[i:])
            stripped_suffix = araby.strip_harakat(token.suffix)
            arab_wo_suffix = arab_tools.join(
                rasm[i : len(rasm) - len(stripped_suffix)],
                harakat[i : len(rasm) - len(stripped_suffix)],
            )

            # nisba
            arab_rasm = araby.strip_diacritics(token.arab)
            lemma_rasm = araby.strip_diacritics(token.lemma)
            token.is_nisba = (
                token.pos == "noun"
                and data.shaddah in harakat[-1]
                and lemma_rasm + data.ya == arab_rasm
            )

            # special cases
            rasm, harakat = arab_tools.separate(token.arab)
            if token.pos == "verb" and verb_ending == "وا" and token.arab.endswith("ا"):
                token.arab = arab_tools.join(rasm[:-1], harakat[:-1])
            elif amru_pattern(token.arab):
                token.arab = araby.strip_lastharaka(
                    arab_tools.join(rasm[:-1], harakat[:-1])
                )
            elif ana_pattern(token.arab):
                token.arab = "أَنَ"
            elif allah_pattern(token.arab):
                token.arab = arab_tools.inject("ا", token.arab, 3)
                token.is_name = (
                    not apply_hamzatul_wasl and not token.prefix and not next_wasl
                )
            elif lillah_pattern(token.arab):
                token.prefix = "لِ"
                token.latin_prefix = "li-"
                token.arab = "للاهِ" if not token.is_pausa else "للاه"
            elif ulaika_pattern1(token.arab) or ulaika_pattern2(token.arab):
                if rasm[3] != "ا":
                    rasm.insert(3, "ا")
                    harakat.insert(3, "")
                token.arab = arab_tools.join(
                    rasm[:1] + rasm[2:], harakat[:1] + harakat[2:]
                )
            elif (
                profile_is_name
                and not profile.is_book
                and (
                    (bint := bint_pattern(token.arab))
                    or ibn_pattern(token.arab)
                    or bin_pattern(token.arab)
                )
            ):
                # women first :)
                if bint:
                    if token_i:
                        token.is_name = False
                        if profile.short_ibn:
                            token.arab = "بت"
                            token.latin_after = "." + token.latin_after
                else:
                    token.arab = data.kasra + "بن"
                    if token_i:
                        token.is_name = False
                        if profile.short_ibn:
                            token.arab = "ب"
                            token.latin_after = "." + token.latin_after
            else:
                for pattern, inserts in add_alif_patterns:
                    if pattern(arab_wo_suffix):
                        for insert in inserts:
                            token.arab = arab_tools.inject("ا", token.arab, insert)
                        break

            # hu & hi
            if (
                profile.hu_hi
                and stripped_suffix == "ه"
                and (h_haraka := token.arab[-1]) in (data.damma, data.kasra)
                and len(token.arab) >= 3
                and rasm[-2] not in data.long_vowels
            ):
                token.arab += data.waw if h_haraka == data.damma else data.ya

            # hamzatul wasl
            # applying hamzatul wasl for next token
            arab = token.arab
            prev_ended_vowel = apply_hamzatul_wasl
            prev_wasl = next_wasl
            apply_hamzatul_wasl = (
                arab[-1] in (data.alif, data.alif_maqsurah)
                and (len(arab) == 1 or arab[-2] != data.fathatan)
                or arab[-1] in data.half_vowels
                and data.half_vowel_is_long(arab, len(arab) - 1)
                or arab[-1] in data.short_vowels
            )
            next_wasl = (
                "u"
                if hum_pattern(arab) or antum_pattern(arab) or hum_pattern(token.suffix)
                else "i"
                if token.pos == "stopword"
                and token.lemma[-1] == data.sukun
                and not min_pattern(arab)
                else ""
            )

            if len(araby.strip_diacritics(arab)) <= 2:
                continue

            # hamzatul wasl for this token
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
                has_haraka = token.arab[0] in data.short_vowels
                if prev_ended_vowel:
                    if has_haraka:
                        token.arab = token.arab[1:]
                elif not has_haraka:
                    if (
                        araby.separate(araby.strip_lastharaka(token.arab))[1][1]
                        == data.damma
                    ):
                        haraka = "u"
                    elif token.arab[0] == "ل":  # TODO: and not matches something else
                        haraka = "a"
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
            if (
                profile_is_name
                and abd_pattern(token.arab)
                and processed_allah_pattern(next_token.arab)
                and not token.suffix
                and not next_token.suffix
                and not token.prefix
                and not next_token.prefix
            ):
                token.latin_after = ""
                next_token.is_name = False

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
        if profile.nisba or token.is_nisba:
            char_map |= data.nisba_map
        rules = [(re.compile(arab), latin) for arab, latin in char_map.items()]
        cont: bool = True
        while cont:
            cont = False
            for pattern, replace in rules:
                word, n = pattern.subn(replace, word)
                cont = cont or bool(n)
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


name_connector_patterns = [
    gen_arab_pattern_match(word) for word in data.ijmes_name_connectors
]


def transliterate_ijmes(text: str, profile: IJMESProfile = IJMESProfile()) -> str:
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
        Token(token, after=text[end:start], is_pausa=True)
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

    last_was_name = False
    for sentence in sentences:
        sentence[-1].is_end_of_sentence = True

        # word analysis and stemming
        stemmed_words = [*arab_tools.check_sentence(sentence)]
        for token, stemming in zip(sentence, stemmed_words):
            (
                token.lemma,
                token.pos,
                token.gram_case,
                token.is_definite,
                prefix_suggestion,
                verb_ending,
                token.suffix,
                _,
            ) = stemming
            assert token.pos in ("noun", "verb", "stopword", "")

            if profile.is_name:
                is_name_connector = any(
                    pattern(token.arab) for pattern in name_connector_patterns
                )
                is_real_name = token.is_name = (
                    token.pos != "stopword" and not is_name_connector
                )
                if is_name_connector:
                    token.is_name = not last_was_name
                # print(token.arab, last_was_name, is_name_connector, is_real_name)
                last_was_name = is_real_name

            # applying pausa
            if token.pos == "noun" and not token.suffix:
                token.arab = araby.strip_lastharaka(token.arab)

            # getting the prefix
            rasm, harakat = arab_tools.separate(token.arab)
            sug_rasm, sug_harakat = arab_tools.separate(prefix_suggestion)
            i = 0  # the index in the rasm

            def get_rasm(i: int) -> str:
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
                elif next_letter in "لبك":
                    if next_letter in "لب" and (
                        not harakat[i] or harakat[i] == data.kasra
                    ):
                        token.latin_prefix += (
                            "l" if next_letter == "ل" else "b"
                        ) + "i-"
                        i += 1
                        # lil
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
            stripped_suffix = araby.strip_harakat(token.suffix)
            arab_wo_suffix = arab_tools.join(
                rasm[i : len(rasm) - len(stripped_suffix)],
                harakat[i : len(rasm) - len(stripped_suffix)],
            )

            # nisba
            arab_rasm = araby.strip_diacritics(token.arab)
            lemma_rasm = araby.strip_diacritics(token.lemma)
            token.is_nisba = (
                token.pos == "noun"
                and data.shaddah in harakat[-1]
                and lemma_rasm + data.ya == arab_rasm
            )

            # special cases
            rasm, harakat = arab_tools.separate(token.arab)
            if token.pos == "verb" and verb_ending == "وا" and token.arab.endswith("ا"):
                token.arab = arab_tools.join(rasm[:-1], harakat[:-1])
            elif amru_pattern(token.arab):
                token.arab = araby.strip_lastharaka(
                    arab_tools.join(rasm[:-1], harakat[:-1])
                )
            elif ana_pattern(token.arab):
                token.arab = "أَنَ"
            elif allah_pattern(token.arab):
                token.arab = arab_tools.inject("ا", token.arab, 3)
                token.is_name = True
            elif lillah_pattern(token.arab):
                token.prefix = "لِ"
                token.latin_prefix = "li-"
                token.arab = "للاهِ" if not token.is_pausa else "للاه"
            elif ulaika_pattern1(token.arab) or ulaika_pattern2(token.arab):
                if rasm[3] != "ا":
                    rasm.insert(3, "ا")
                    harakat.insert(3, "")
                token.arab = arab_tools.join(
                    rasm[:1] + rasm[2:], harakat[:1] + harakat[2:]
                )
            else:
                for pattern, inserts in add_alif_patterns:
                    if pattern(arab_wo_suffix):
                        for insert in inserts:
                            token.arab = arab_tools.inject("ا", token.arab, insert)
                        break

            if len(rasm) > 2 and token.arab[0] in (
                data.alif,
                data.alif_wasl,
            ):
                token.arab = token.arab[1:]
                has_haraka = token.arab[0] in data.short_vowels
                if not has_haraka:
                    if (
                        araby.separate(araby.strip_lastharaka(token.arab))[1][1]
                        == data.damma
                    ):
                        haraka = "u"
                    elif token.arab[0] == "ل":  # TODO: and not matches something else
                        haraka = "a"
                    else:
                        haraka = "i"
                    token.arab = haraka + token.arab

        # idafah
        for token, next_token in zip(sentence, sentence[1:]):
            token.is_idafah = (
                token.pos == "noun"
                and not token.latin_prefix.endswith("l-")
                and token.is_definite
                and not token.suffix
                and token.after.isspace()  # there can't be anything else (like numbers, etc.) between
                and next_token.is_genetive
                and next_token.latin_prefix in ("al-", "l-", "")
            )
            if (
                profile.is_name
                and abd_pattern(token.arab)
                and processed_allah_pattern(next_token.arab)
                and not token.suffix
                and not next_token.suffix
                and not token.prefix
                and not next_token.prefix
            ):
                token.latin_after = ""
                next_token.is_name = False

    # transliteration
    for token in tokens:
        word = token.arab
        # char mapping
        char_map = (
            data.subs | data.vowel_map | data.begin_hamza_map | data.ijmes_con_map
        )
        if not token.is_idafah:
            char_map["ة"] = ""
        if token.is_nisba:
            char_map["iyy$"] = "iyya"
        if profile.diphthongs:
            char_map |= data.diphthong_map
        if profile.is_name:
            char_map |= data.ijmes_name_map
        rules = [(re.compile(arab), latin) for arab, latin in char_map.items()]
        cont: bool = True
        while cont:
            cont = False
            for pattern, replace in rules:
                word, n = pattern.subn(replace, word)
                cont = cont or bool(n)
                # if n:
                #     print(word, pattern, replace)
        prefix = token.latin_prefix

        if (first_letter := word[0]) in data.sun_letters:
            if len(word) >= 2 and word[1] == first_letter:
                word = word[1:]
        token.latin = word

    return beginning_non_token + "".join(token.result for token in tokens)

def transliterate_llm(text: str):
    from huggingface_hub import InferenceClient

    input_words = text.split().__len__()

    # no special key
    client = InferenceClient(
        provider="nscale",
        token=os.environ["HF_TOKEN"]
    )

    messages = [
        {
            "role": "system",
            "content":  """
                        
                        You are a transliterator that transliterates vocalized or unvocalized Arabic text according to the IJMES standard. 
                        Your task is to transliterate as succinctly as possible. 
                        
                        To correctly transliterate, you must first understand the meaning of the text, its grammatical structure, and the context in which words are used.

                        Don't explain anything, keep your answers as short as possible. 
                        """.strip()
        },
        {
            "role": "user",
            "content": text
        }
    ]

    completion = client.chat_completion(
        model="Qwen/Qwen3-235B-A22B", 
        messages=messages, 
        max_tokens=input_words*200 + 2000,
        temperature=0.6,
        top_p=0.95,
    )

    content = completion.choices[0].message.content

    if content is None:
        raise ValueError("No content returned from LLM.")

    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

    return content.strip()