"""
Extracting the essentials from linuxscouts arabic libraries
"""

from functools import cache
from typing import Literal
from pyarabic import araby
import naftawayh.wordtag
import naftawayh.wordtag_const as wordtag_const
import qalsadi.stemmedword as stemmedword
import qalsadi.disambig as disambig
# import tashaphyne.stemming
# stemmer = tashaphyne.stemming.ArabicLightStemmer()

remove_i3rab = araby.strip_lastharaka


def normalize(text: str) -> str:
    """
    Normalize Arabic text
    """
    text = araby.strip_tatweel(text)
    text = araby.normalize_ligature(text)
    text = araby.normalize_hamza(text)
    text = araby.normalize_alef(text)
    # autocorrect and fix_spaces are a bit opaque
    # text = araby.fix_spaces(text)
    # text = araby.autocorrect(text)
    return text


_tokenize = araby.tokenize_with_location


def tokenize_with_location(text: str) -> list[str]:
    """
    Tokenizes Arabic text with the tokens location and without any empty tokens

    From:
    qalsadi.analex.Analex.text_tokenize
    """
    return [x for x in _tokenize(text) if x["token"]]


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

    tag_word works similarly to the original one_word_tagging but doesn't append digits to the tag
    """

    @cache
    def tag_word_alone(self, word: str) -> Tag:
        """
        Tags an Arabic word without any context
        """
        stripped_word = araby.strip_tashkeel(araby.strip_tatweel(word))
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
            elif previous in wordtag_const.tab_noun_context:
                return "n"
            if second_previous and (
                second_previous in wordtag_const.tab_noun_context
                or second_previous in wordtag_const.tab_noun_context
            ):
                return "t"
        return tag


tagger = WordTagger()

disambiguator = disambig.Disambiguator()


def check_word(word: str, tag: str) -> list[str]:
    """
    Analyzes an Arabic word

    From:
    qalsadi.analex.Analex.check_word
    """


def check_words(tokens: list[str]) -> list[dict]:
    """
    Analyzes Arabic tokens

    From:
    qalsadi.analex.Analex.check_text
    """
    guessed_tags = tagger.word_tagging(tokens)

    if len(guessed_tags) != len(tokens):
        guessed_tags = ["nv"] * len(tokens)

    if False:
        newwordlist = disambiguator.disambiguate_words(tokens, guessed_tags)

        # avoid the incomplete list
        if len(newwordlist) == len(tokens):
            list_word = newwordlist

    resulted_data = []

    for word, tag in zip(list_word, guessed_tags):
        one_data_list = check_word(word, tag)
        stemmed_one_data_list = [stemmedword.StemmedWord(w) for w in one_data_list]
        resulted_data.append(stemmed_one_data_list)
    return resulted_data
