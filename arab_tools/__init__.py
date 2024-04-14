"""
# Arab Tools

Arab tools is a module that uses the essentials from Taha Zerroukis (aka linuxscout) Arabic libraries.

The changes were mainly to
- clean up the code,
- make it Python 3,
- remove unnecessary OOP,
- remove prints,
- remove caching,
- etc.

The files in this module are licensed under the GPL-3.0 License.

"""

from functools import cache
from typing import Literal

import asmai.semdictionary
import naftawayh.wordtag
import naftawayh.wordtag_const as wordtag_const
import qalsadi.analex_const as analex_const
import qalsadi.stem_verb
import qalsadi.stopwords
from pyarabic import araby
from qalsadi.stem_stop import StopWordStemmer
from qalsadi.stem_unknown import UnknownStemmer
from qalsadi.stemmedword import StemmedWord
from qalsadi.wordcase import WordCase

import data
from data_types import Sentence, Token

from .nounstemmer import stem_noun

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
        stamp = self.verb_dictionary.word_stamp(word)
        return data.verb_dict[stamp]

    def exists_as_stamp(self, word):
        """
        lookup for word in dict
        """
        stamp = self.verb_dictionary.word_stamp(word)
        stamp = stamp.replace(araby.TEH, "")
        # a verb stamp can't more than 4 letters
        if len(stamp) > 4:
            return False
        return stamp in data.verb_dict


class SemanticDictionary(asmai.semdictionary.SemanticDictionary):
    def get_original(self, primate_word):
        return data.sem_derivations.get(primate_word, ("", ""))


# Fix qalsadi and asmai from here
qalsadi.stem_verb.VerbStemmer = VerbStemmer
asmai.semdictionary.SemanticDictionary = SemanticDictionary

tagger = WordTagger()
verbstemmer = VerbStemmer()
unknownstemmer = UnknownStemmer()
stopwordstemmer = StopWordStemmer()


def get_freq(word, wordtype):
    """
    Words frequency
    """
    return data.freq_dict.get((word, wordtype), 0)


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
            result += stem_noun(word_nm)

    if not result:
        result = unknownstemmer.stemming_noun(word_nm)

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

    # if not result:
    #     debug("No result for", word, tag, word_nm, word_nm_shadda)

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
