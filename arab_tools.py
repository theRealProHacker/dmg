"""
Extracting the essentials from linuxscouts arabic libraries
"""

from functools import cache
from typing import Literal
from pyarabic import araby
import naftawayh.wordtag
import naftawayh.wordtag_const as wordtag_const
from qalsadi.stemmedword import StemmedWord
from qalsadi.wordcase import WordCase
import qalsadi.analex
from qalsadi.stem_noun import NounStemmer
from qalsadi.stem_verb import VerbStemmer
from qalsadi.stem_unknown import UnknownStemmer
from qalsadi.stem_stop import StopWordStemmer
from qalsadi.stem_pounct_const import POUNCTUATION as PUNCTUATION
import qalsadi.stopwords
import qalsadi.analex_const as analex_const
from arramooz import wordfreqdictionaryclass
# import tashaphyne.stemming
# stemmer = tashaphyne.stemming.ArabicLightStemmer()

remove_i3rab = araby.strip_lastharaka


def normalize(text: str) -> str:
    """
    Normalizes Arabic text by replacing common ligatures and beautifications
    and normalizing the hamza and alef characters
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


def tokenize_with_location(
    text: str,
) -> tuple[tuple[str, ...], tuple[int, ...], tuple[int, ...]]:
    """
    Tokenizes Arabic text with the tokens location and without any empty tokens

    From:
    qalsadi.analex.Analex.text_tokenize

    Usage
    ```py
    tokens, starts, ends = tokenize_with_location(text)
    ```
    """
    return zip(*([*x.values()] for x in _tokenize(text) if x["token"]))


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


tagger = WordTagger()
nounstemmer = NounStemmer()
verbstemmer = VerbStemmer()
unknownstemmer = UnknownStemmer()
stopwordstemmer = StopWordStemmer()
# freq_dict = wordfreqdictionaryclass.WordFreqDictionary(
#     "wordfreq", wordfreqdictionaryclass.WORDFREQ_DICTIONARY_INDEX
# )


class Analex:
    """
    This Analex tries to improve on the qalsadi version by removing the cache and making the steps more clear

    Also, this is an implicit singleton, so please don't create multiple instances
    -> To solve this, this class will be resolved soon and turned into a module
    """

    @staticmethod
    def get_error_code():
        """
        Return error code when word is not recognized
        """
        return f"N{nounstemmer.get_error_code()}-V{verbstemmer.get_error_code()}"

    @staticmethod
    @cache
    def get_freq(word, wordtype):
        """
        Words frequency
        """
        return 0  # we don't want to access the file system
        return freq_dict.get_freq(word, wordtype)

    @staticmethod
    def check_word_as_numeric(word: str) -> StemmedWord | None:
        # TODO: fix it to isdigit, by moatz saad
        if word.isnumeric():
            return StemmedWord(
                {
                    "word": word,
                    "affix": ("", "", "", ""),
                    "stem": "",
                    "original": word,
                    "vocalized": word,
                    "tags": "عدد",
                    "type": "NUMBER",
                    "freq": 0,
                    "syntax": "",
                    "root": "",
                }
            )
        return None

    @staticmethod
    def check_word_as_punct(word: str) -> StemmedWord | None:
        """
        Check if the word is  punctuation
        """
        if all(char in PUNCTUATION for char in word):
            # if all chars are punctuation, the word takes tags of the first char
            return StemmedWord(
                {
                    "word": word,
                    "affix": ("", "", "", ""),
                    "stem": "",
                    "original": word,
                    "vocalized": word,
                    "tags": PUNCTUATION[word[0]]["tags"],
                    "type": "POUNCT",
                    "freq": 0,
                    "syntax": "",
                    "root": "",
                }
            )

    @staticmethod
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
                    is_verb
                    and word.endswith(araby.KASRA)
                    and output.endswith(araby.SUKUN)
                ):
                    if araby.vocalizedlike(word[:-1], output[:-1]):
                        item["tags"] += ":" + analex_const.PARTIAL_VOCALIZED_TAG
                        filtered.append(item)
        return filtered

    @cache
    def check_word(self, word: str, tag: str) -> list[StemmedWord]:
        """
        Analyzes an Arabic word by going through all possible cases
        (number, punctuation, stopword, verb, noun and unknown)

        Assumes that the word is vocalized, normalized and not empty

        From:
        qalsadi.analex.Analex.check_word
        """
        word_nm = araby.strip_tashkeel(word)
        word_nm_shadda = araby.strip_harakat(word)

        if stemmed := self.check_word_as_numeric(word_nm):
            return [stemmed]

        if stemmed := self.check_word_as_punct(word_nm):
            return [stemmed]

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
            result = unknownstemmer.stemming_noun(word_nm)

        result = [
            x
            for x in result
            if araby.shaddalike(word_nm_shadda, x.vocalized)
            and x.unvocalized == word_nm
        ]

        result = self.check_partially_vocalized(word, result)

        for item in result:
            freqtype = item.freq
            if freqtype == "freqverb":
                wordtype = "verb"
            elif freqtype == "freqnoun":
                wordtype = "noun"
            elif freqtype == "freqstopword":
                wordtype = "stopword"
            else:
                continue
            item.freq = self.get_freq(item.original, wordtype)

        if not result:
            error_code = self.get_error_code()
            return StemmedWord(
                {
                    "word": word,
                    "affix": ("", "", "", ""),
                    "stem": word,
                    "original": word,
                    "vocalized": word,
                    "semivocalized": word,
                    "tags": error_code,
                    "type": "unknown",
                    "root": "",
                    "template": "",
                    "freq": self.get_freq(word, "unknown"),
                    "syntax": "",
                    # addition
                    "number": ()
                }
            )

        return [StemmedWord(w) for w in result]

    def check_words(self, tokens: list[str]) -> list[list[StemmedWord]]:
        """
        Analyzes Arabic tokens

        From:
        qalsadi.analex.Analex.check_text
        """
        guessed_tags = [tagger.tag_word(token) for token in tokens]

        return [self.check_word(word, tag) for word, tag in zip(tokens, guessed_tags)]

if __name__ == "__main__":
    text = "يَكْتُبُ الكَلْبُ"

    print(normalize(text))

    tokens, starts, ends = tokenize_with_location(text)
    print(tokens, starts, ends)

    analex = Analex()

    analyzed = analex.check_words(tokens)
    print(analyzed)