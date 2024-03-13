"""
Extracting the essentials from linuxscouts arabic libraries
"""

from functools import cache
from logging import debug
from typing import Literal

import naftawayh.wordtag
import naftawayh.wordtag_const as wordtag_const
import qalsadi.analex
import qalsadi.analex_const as analex_const
import qalsadi.stem_noun
import qalsadi.stem_verb
import qalsadi.stopwords
from pyarabic import araby
from qalsadi.stem_stop import StopWordStemmer
from qalsadi.stem_unknown import UnknownStemmer
from qalsadi.stemmedword import StemmedWord
from qalsadi.wordcase import WordCase

import data
from data_types import Sentence, Token

remove_i3rab = araby.strip_lastharaka


Tag = Literal["t", "v", "n", "nv"]
"""
't' for stopwords, 
'v' for verbs, 
'n' for nouns, 
'nv' for ambiguous words
"""


class WordTagger(naftawayh.wordtag.WordTagger):
    """
    This WordTagger is a subclass of naftawayh.wordtag.WordTagger
    and tries to improve on it by adding the functions tag_word_alone and tag_word

    tag_world_alone is cached using functools.cache

    tag_word works similarly to the original one_word_tagging
    but doesn't append digits to the tag
    """

    @cache
    def tag_word_alone(self, word: str) -> Tag:
        """
        Tags an Arabic word without any context
        """
        stripped_word = araby.strip_tashkeel(word)
        if self.is_stopword(stripped_word):
            return "t"
        tag = ""
        if self.is_noun(word):
            tag += "n"
        if self.is_verb(word):
            tag += "v"
        return tag or "nv"

    def tag_word(self, word: str, previous: str = "", second_previous: str = ""):
        """
        Tags an Arabic word using the optional previous and second_previous word
        """
        tag = self.tag_word_alone(word)
        if tag == "nv" and previous:
            if previous in wordtag_const.tab_verb_context:
                return "v"
            if previous in wordtag_const.tab_noun_context:
                return "n"
            if second_previous and second_previous in wordtag_const.tab_noun_context:
                return "t"
        return tag


class VerbStemmer(qalsadi.stem_verb.VerbStemmer):
    def lookup_by_stamp(self, word):
        """
        lookup for word in dict
        """
        if word in self.verb_cache:
            return self.verb_cache[word]
        else:
            result = self.verb_dictionary.lookup_by_stamp(word)
            # remove this line to avoid SQLite call
            # result += self.custom_verb_dictionary.lookup_by_stamp(word)
            self.verb_cache[word] = result
        return result

    def exists_as_stamp(self, word):
        """
        lookup for word in dict
        """
        stamp = self.verb_dictionary.word_stamp(word)
        stamp = stamp.replace(araby.TEH, "")
        # a verb stamp can't more than 4 letters
        # لا يمكن للفعل أن يكون فيه أكثر من أربعة حروف أصلية
        if len(stamp) > 4:
            return False
        if stamp not in self.stamp_cache:
            result = self.verb_dictionary.exists_as_stamp(word)
            # remove this line to avoid SQLite call
            # result +=  self.custom_verb_dictionary.exists_as_stamp(word)
            self.stamp_cache[stamp] = result
        return self.stamp_cache.get(stamp, False)


class NounStemmer(qalsadi.stem_noun.NounStemmer):
    def lookup_dict(self, word):
        """
        lookup for word in dict
        """
        if word in self.noun_cache:
            return self.noun_cache[word]
        else:
            result = self.noun_dictionary.lookup(word)
            # Avoid SQLite call
            # result +=  self.custom_noun_dictionary.lookup(word)
            self.noun_cache[word] = result
        return result


tagger = WordTagger()
nounstemmer = NounStemmer()
verbstemmer = VerbStemmer()
unknownstemmer = UnknownStemmer()
stopwordstemmer = StopWordStemmer()


freq_dict = {}

for entry in data.read("data/wordfreq.json"):
    freq_dict[(entry["vocalized"], entry["word_type"])] = entry["freq"]
    freq_dict[(entry["unvocalized"], entry["word_type"])] = entry["freq"]


def get_freq(word, wordtype):
    """
    Words frequency
    """
    return freq_dict.get((word, wordtype), 0)


def check_partially_vocalized(word: str, data: list[WordCase]) -> list[WordCase]:
    if not araby.is_vocalized(word):
        return data
    filtered = []
    for item in data:
        if "vocalized" in item:
            output = item["vocalized"]
            is_verb = "Verb" in item["type"]
            if araby.vocalizedlike(word, output):
                item["tags"] += ":" + analex_const.PARTIAL_VOCALIZED_TAG
                filtered.append(item)
                # حالة التقا الساكنين، مع نص مشكول مسبقا، والفعل في آخره كسرة بدل السكون
            elif (
                is_verb and word.endswith(araby.KASRA) and output.endswith(araby.SUKUN)
            ):
                if araby.vocalizedlike(word[:-1], output[:-1]):
                    item["tags"] += ":" + analex_const.PARTIAL_VOCALIZED_TAG
                    filtered.append(item)
    return filtered


def possible_prefixes(arabic_word: str, guess: str | None = None) -> list[str]:
    guess = guess or arabic_word[:-1]
    max_prefix_length = len(guess)
    return [
        possible_prefix
        for prefix_length in data.prefix_lengths
        if (
            prefix_length <= max_prefix_length
            and arabic_word.startswith(possible_prefix := guess[:prefix_length])
            and possible_prefix in data.prefixes
        )
    ]


@cache
def check_word(word: str, tag: str) -> list[StemmedWord]:
    """
    Analyzes an Arabic word by going through all possible cases
    (number, punctuation, stopword, verb, noun and unknown)

    Assumes that the word is vocalized, normalized and not empty

    From:
    qalsadi.analex.Analex.check_word
    """
    # print("Checking", word, tag)
    word_nm = araby.strip_tashkeel(word)
    word_nm_shadda = araby.strip_harakat(word)

    result = []

    if araby.is_arabicword(word_nm):
        if word in qalsadi.stopwords.STOPWORDS:
            result += stopwordstemmer.stemming_stopword(word_nm)
        if not any(c in ("ة", *araby.TANWIN) for c in word) and (
            tagger.has_verb_tag(tag) or tagger.is_stopword_tag(tag)
        ):
            result += verbstemmer.stemming_verb(word_nm)
        if tagger.has_noun_tag(tag) or tagger.is_stopword_tag(tag):
            result += nounstemmer.stemming_noun(word_nm)

    if not result:
        result = (
            unknownstemmer.stemming_noun(word_nm)
            or nounstemmer.stemming_noun(word_nm)
            or verbstemmer.stemming_verb(word_nm)
            or stopwordstemmer.stemming_stopword(word_nm)
        )

    result = [
        x
        for x in result
        if araby.shaddalike(word_nm_shadda, x.vocalized) and x.unvocalized == word_nm
    ]

    result = check_partially_vocalized(word, result)

    for item in result:
        # item.freq is a string and becomes a number
        if isinstance(item.freq, str) and len(item.freq) > 4:
            item.freq = get_freq(item.original, item.freq[4:])

    if not result:
        debug("No result for", word, tag, word_nm, word_nm_shadda)

    return [StemmedWord(w) for w in result]


def check_sentence(sentence: Sentence) -> list[list[StemmedWord]]:
    """
    Analyzes Arabic tokens

    From:
    qalsadi.analex.Analex.check_text
    """
    tokens = [token.arab for token in sentence]
    prev_tokens = ["", *tokens]
    prev_prev_tokens = ["", "", *tokens]
    guessed_tags = [
        tagger.tag_word(token, prev, prev_prev)
        for token, prev, prev_prev in zip(tokens, prev_tokens, prev_prev_tokens)
    ]

    result = []
    for token, tag in zip(sentence, guessed_tags):
        preliminary_result = check_word(token.arab, tag)
        # if not preliminary_result:
        #     for prefix in possible_prefixes(token.arab):
        #         preliminary_result = check_word(token.arab[len(prefix) :], tag)
        #         if preliminary_result:
        #             token.prefix = prefix
        #             break
        result.append(preliminary_result)
    return result


def is_hamzatul_wasl(token: Token) -> bool:
    """
    Checks if a word starts with hamzatul wasl

    Assumes the word starts with a hamza
    """
    assert token.arab[0] == data.hamza or token.arab[0] == data.alif
    test_word = token.arab[1:]
    return False and test_word
