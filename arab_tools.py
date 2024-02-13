"""
Extracting the essentials from linuxscouts arabic libraries
"""

from functools import cache
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

# from arramooz import wordfreqdictionaryclass
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
        # return freq_dict.get_freq(word, wordtype)

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
        # print("Checking", word, tag)
        word_nm = araby.strip_tashkeel(word)
        word_nm_shadda = araby.strip_harakat(word)

        if stemmed := self.check_word_as_numeric(word_nm):
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
            result = (
                unknownstemmer.stemming_noun(word_nm)
                or nounstemmer.stemming_noun(word_nm)
                or verbstemmer.stemming_verb(word_nm)
                or stopwordstemmer.stemming_stopword(word_nm)
            )

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
            print("No result for", word, tag, word_nm, word_nm_shadda)

        return [StemmedWord(w) for w in result]

    def check_words(self, tokens: list[str]) -> list[list[StemmedWord]]:
        """
        Analyzes Arabic tokens

        From:
        qalsadi.analex.Analex.check_text
        """
        prev_tokens = ["", *tokens]
        prev_prev_tokens = ["", "", *tokens]
        guessed_tags = [
            tagger.tag_word(token, prev, prev_prev)
            for token, prev, prev_prev in zip(tokens, prev_tokens, prev_prev_tokens)
        ]

        return [self.check_word(word, tag) for word, tag in zip(tokens, guessed_tags)]


if __name__ == "__main__":
    text = "يَكْتُبُ الكَلْبُ"

    print(normalize(text))

    tokens, starts, ends = tokenize_with_location(text)
    print(tokens, starts, ends)

    analex = Analex()

    analyzed = analex.check_words(tokens)
    print(analyzed)
