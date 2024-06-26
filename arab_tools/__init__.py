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
import itertools
from typing import Callable, Generator, Literal

import asmai.semdictionary
import naftawayh.wordtag
import naftawayh.wordtag_const as wordtag_const
import qalsadi.analex_const as analex_const
import qalsadi.stem_stop
import qalsadi.stem_unknown
import qalsadi.stem_verb
import qalsadi.stopwords
from pyarabic import araby
from qalsadi import stemnode
from qalsadi import stem_stopwords_const as ssconst
from qalsadi.stemmedword import StemmedWord
from qalsadi.wordcase import WordCase

import data
from data_types import Case, Pos, Sentence, Token

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
        # a verb stamp can't be more than 4 letters
        if len(stamp) > 4:
            return False
        return stamp in data.verb_dict


class UnknownStemmer(qalsadi.stem_unknown.UnknownStemmer):
    def lookup_dict(self, word):
        result = []
        if item := data.unknown_dict.get(word):
            result.append(item)
        # if result:
        #     print(result)
        return result


class StopWordStemmer(qalsadi.stem_stop.StopWordStemmer):
    def steming_second_level(self, stop, stop2, procletic, encletic_nm):
        """
        Analyze word morphologically by stemming the conjugation affixes.
        @param stop: the input stop.
        @type stop: unicode.
        @param stop2: the stop stemed from syntaxic affixes.
        @type stop2: unicode.
        @param procletic: the syntaxic prefixe extracted in the fisrt stage.
        @type procletic: unicode.
        @param encletic_nm: the syntaxic suffixe extracted in the
        first stage (not vocalized).
        @type encletic_nm: unicode.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        detailed_result = []
        #segment the coinjugated verb
        list_seg_conj = self.conj_stemmer.segment(stop2)
        # verify affix compatibility
        list_seg_conj = self.verify_affix(stop2, list_seg_conj,
                                     ssconst.STOPWORDS_CONJUGATION_AFFIX)
        # add vocalized forms of suffixes
        # and create the real affixes from the word
        #~list_seg_conj_voc = []
        for seg_conj in list_seg_conj:
            stem_conj = stop2[seg_conj[0]:seg_conj[1]]
            suffix_conj_nm = stop2[seg_conj[1]:]

            # noirmalize hamza before gessing  differents origines
            #~stem_conj = araby.normalize_hamza(stem_conj)

            # generate possible stems
            # add stripped letters to the stem to constitute possible stop list
            possible_stop_list = self.get_stem_variants(stem_conj, suffix_conj_nm)

            # search the stop in the dictionary
            # we can return the tashkeel
            infstop_form_list = []
            for infstop in set(possible_stop_list):
                # get the stop and get all its forms from the dict
                # if the stop has plural suffix, don't look up in
                #broken plural dictionary
                if infstop not in self.cache_dict_search:
                    infstop_foundlist = data.stopword_dict.get(infstop, [])
                    # _infstop_foundlist = list(map(dict, self.stop_dictionary.lookup(infstop)))
                    # for x in _infstop_foundlist:
                    #     x.pop("ID")
                    # assert _infstop_foundlist == infstop_foundlist, (
                    #     infstop, _infstop_foundlist, infstop_foundlist
                    # )
                    self.cache_dict_search[infstop] = self.create_dict_word(
                        infstop_foundlist)
                else:
                    infstop_foundlist = self.cache_dict_search[infstop]
                infstop_form_list.extend(infstop_foundlist)
            for stop_tuple in infstop_form_list:
                # stop_tuple = self.stop_dictionary.getEntryById(id)
                original = stop_tuple['vocalized']

                #test if the  given word from dictionary accept those
                # tags given by affixes
                # دراسة توافق الزوائد مع خصائص الاسم،
                # مثلا هل يقبل الاسم التأنيث.
                #~if validate_tags(stop_tuple, affix_tags, procletic, encletic_nm, suffix_conj_nm):
                for vocalized_encletic in ssconst.COMP_SUFFIX_LIST_TAGS[
                        encletic_nm]['vocalized']:
                    for vocalized_suffix in ssconst.CONJ_SUFFIX_LIST_TAGS[
                            suffix_conj_nm]['vocalized']:
                        # affixes tags contains prefixes and suffixes tags
                        affix_tags = ssconst.COMP_PREFIX_LIST_TAGS[procletic]['tags'] \
                                  +ssconst.COMP_SUFFIX_LIST_TAGS[vocalized_encletic]['tags'] \
                                  +ssconst.CONJ_SUFFIX_LIST_TAGS[vocalized_suffix]['tags']
                        ## verify compatibility between procletics and affix
                        valid = self.validate_tags(stop_tuple, affix_tags, procletic, encletic_nm)
                        compatible = self.is_compatible_proaffix_affix(
                            stop_tuple, procletic, vocalized_encletic,
                            vocalized_suffix)
                        if valid and compatible:
                            vocalized_list = self.vocalize(
                                original, procletic, vocalized_suffix,
                                vocalized_encletic)
                            vocalized, semi_vocalized =   vocalized_list[0][0],  vocalized_list[0][1]                              
                            vocalized = self.ajust_vocalization(vocalized)
                            #ToDo:
                            # if the stop word is inflected or not
                            is_inflected = u"مبني" if stop_tuple[
                                'is_inflected'] == 0 else u"معرب"
                            #add some tags from dictionary entry as
                            # use action and object_type
                            original_tags = u":".join([
                                stop_tuple['word_type'],
                                stop_tuple['word_class'],
                                is_inflected,
                                stop_tuple['action'],
                            ])
                            #~print "STOP_TUPEL[action]:", stop_tuple['action'].encode("utf8")
                            # generate word case
                            detailed_result.append(
                                WordCase({
                                    'word':
                                    stop,
                                    'affix': (procletic, '', vocalized_suffix,
                                              vocalized_encletic),
                                    'stem':
                                    stem_conj,
                                    'original':
                                    original,
                                    'vocalized':
                                    vocalized,
                                    'semivocalized':
                                    semi_vocalized,                                     
                                    'tags':
                                    u':'.join(affix_tags),
                                    'type':
                                    u':'.join(
                                        ['STOPWORD', stop_tuple['word_type']]),
                                    'freq':
                                    'freqstopword',  # to note the frequency type
                                    'originaltags':
                                    original_tags,
                                    "action":
                                    stop_tuple['action'],
                                    "object_type":
                                    stop_tuple['object_type'],
                                    "need":
                                    stop_tuple['need'],
                                    'syntax':
                                    '',
                                }))
        return detailed_result


class SemanticDictionary(asmai.semdictionary.SemanticDictionary):
    def get_original(self, primate_word):
        return data.sem_derivations.get(primate_word, ("", ""))


# Fix qalsadi and asmai from here
qalsadi.stem_verb.VerbStemmer = VerbStemmer
qalsadi.stem_unknown.UnknownStemmer = UnknownStemmer
qalsadi.stem_stop.StopWordStemmer = StopWordStemmer
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
    word_nm = araby.strip_tashkeel(word)
    word_nm_shadda = araby.strip_harakat(word)

    result = []

    if araby.is_arabicword(word_nm):
        if word_nm in qalsadi.stopwords.STOPWORDS:
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
            item.freq = get_freq(item.unvocalized, item.freq[4:])

    return [StemmedWord(w) for w in result]


def check_sentence(sentence: Sentence)->Generator[tuple[str, Pos, Case, bool, str, str, str], None, None]:
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

    for token, tag in zip(sentence, guessed_tags):
        preliminary_result = check_word(token.arab, tag)
        # lemma, pos, case, is_definite, prefix, verb ending, suffix
        if not preliminary_result:
            # print(token.arab, "not found")
            yield (
                araby.strip_diacritics(token.arab),
                "noun",
                *data.case_mapping.get(token.arab[-1], ("n", True)),
                "",
                "",
                ""
            )
        else:
            result = preliminary_result
            node = stemnode.StemNode(result, True)
            sm = node.syntax_mark
            cases: dict[Case, int] = {
                "n": len(sm["marfou3"]) + len(sm["tanwin_marfou3"]),
                "a": len(sm["mansoub"]) + len(sm["tanwin_mansoub"]),
                "g": len(sm["majrour"]) + len(sm["tanwin_majrour"]),
                "j": len(sm["majzoum"]),
            }
            sorted_cases = sorted(cases, key=cases.get, reverse=True)
            gram_case = (
                ""
                if cases[sorted_cases[0]] == cases[sorted_cases[1]]
                else sorted_cases[0]
            )
            # give preference
            is_definite = len(sm["marfou3"]) + len(sm["mansoub"]) + len(
                sm["majrour"]
            ) >= len(sm["tanwin_marfou3"]) + len(sm["tanwin_mansoub"]) + len(
                sm["tanwin_majrour"]
            )
            affix = node.get_affix().split("-")
            # print(affix)
            # print((
            #     *node.get_lemma(return_pos=True),
            #     gram_case,
            #     is_definite,
            #     affix[0],
            #     *affix[2:4]
            # ))
            yield (
                *node.get_lemma(return_pos=True),
                gram_case,
                is_definite,
                affix[0],
                *affix[2:4]
            )


def is_hamzatul_wasl(token: Token) -> bool:
    """
    Checks if a word starts with hamzatul wasl

    Assumes the word starts with an alif
    """
    assert token.arab[0] == data.alif
    test_word = token.arab[1:]
    raise NotImplementedError

def separate(word: str) -> tuple[list[str], list[str]]:
    """
    Splits a word into the rasm and the harakat
    """
    pos = -1
    rasm = []
    harakat = []
    for c in word:
        if c in data.harakat:
            if not rasm:
                rasm.append("")
                harakat.append("")
                pos += 1
            harakat[pos] += c
        else:
            pos += 1
            rasm.append(c)
            harakat.append("")
    return rasm, harakat

def join(rasm: list[str], harakat: list[str]) -> str:
    """
    Joins the rasm and the harakat into a word
    """
    return "".join(itertools.chain(*zip(rasm, harakat)))

def inject(injection: str, word: str, pos: int):
    """
    Inject a string into a word at a specific (rasm) position
    """
    _, harakat = separate(word)
    actual_pos = pos + sum(len(r) for r in harakat[:pos])
    return word[:actual_pos] + injection + word[actual_pos:]

def remove_rasm(word: str, pos: int):
    rasm, harakat = separate(word)
    return join(rasm[:pos]+rasm[pos+1:], harakat[:pos]+harakat[pos+1:])


def gen_arab_pattern_match(word: str) -> Callable[[str], bool]:
    """
    Generates a pattern for a word
    """
    rasm, harakat = separate(word)

    def match_pattern(word: str) -> bool:
        test_rasm, test_harakat = separate(word)
        return test_rasm == rasm and all(
            not t or not h or h == t for h, t in zip(harakat, test_harakat)
        )

    return match_pattern
