from dataclasses import dataclass
import re
import data
from typing import Literal

from pyarabic import araby
import qalsadi.lemmatizer
import qalsadi.analex

analex = qalsadi.analex.Analex()
lemmatizer = qalsadi.lemmatizer.Lemmatizer()
lemmatizer.set_vocalized_lemma()

Pos = Literal["stopword", "noun", "verb"]


@dataclass
class Profile:
    pausa: bool = False
    ta_marbatuh: bool = False
    # skip_i3rab: bool = False
    # """Whether i3rab (flexion endings) should be skipped"""
    # full_vocalisation: bool = False
    # """ Full vocalised transcription"""
    # TODO: Diphtonge: aw -> au
    # TODO: niyyah -> nīyah, awwal -> auwal
    # TODO: imalah, ishmam
    # TODO: alif maqsura to ya
    # TODO: Zwei Doppelpunkte bei emphatischen Konsonanten
    # TODO: alif maqsura mit Unterpunkt

    descriptions = {
        "pausa": ("Pausa", "Ob der Text in Pausa gelesen werden soll"),
        "ta_marbatuh": (
            "Ta marbuta",
            "Ob die Ta marbuta am Ende eines Wortes wiedergegeben werden soll",
        ),
    }


@dataclass
class Token:
    arab: str
    lemma: str
    pos: Pos
    is_pausa: bool = False
    latin: str = ""
    prefix: str = ""
    latin_prefix: str = ""
    is_name: bool = False
    is_part_of_idafah: bool = False
    starts_with_hamzatul_wasl: bool = False

    def determine_prefix(self):
        """
        Determines whether the token begins with a prefix
        and sets the prefix attribute accordingly
        """
        # for length in data.prefix_lengths:
        #     # TODO: check if this works for small words
        #     if self.latin[:length] in data.prefixes:
        #         self.prefix = self.latin[:length]
        #         self.latin = self.latin[length:]
        #         break

    def map_chars(self):
        """
        Replaces the arab chars with latin chars
        and sets the latin attribute accordingly
        """
        char_map = (
            data.subs | data.diacritic_map | data.char_map | data.special_char_map
        )
        # if self.is_pausa:
        #     char_map = data.pausa_map | char_map | data.pausa_map
        rules = [(re.compile(arab), latin) for arab, latin in char_map.items()]
        word = self.arab
        if self.is_pausa:
            word = araby.strip_lastharaka(word)
        cont: bool = True
        while cont:
            cont = False
            for pattern, replace in rules:
                word, n = pattern.subn(replace, word)
                if n:
                    print(n, word, pattern, replace)
                    cont = True
        self.latin = word

    def capitalize(self):
        """
        Determines whether the transliterated word is a proper name
        and sets the is_name attribute accordingly
        """
        # TODO: this can only work using the arabic lemma
        # self.is_name = self.latin in data.proper_names

    def assimilate(self):
        """
        Apply internal assimilations to the latin
        """
        # sun letter assimilation
        first_letter = self.latin[0]
        if self.prefix.endswith("al") and first_letter in data.sun_letters:
            self.prefix = self.prefix[:-1] + first_letter

    def result(self):
        """
        Returns the transliterated word
        """
        if self.is_name:
            self.latin = self.latin.capitalize()
        return (self.prefix + "-" if self.prefix else "") + self.latin


def tokenize(text: str, profile: Profile) -> list[Token]:
    """
    Tokenizes the `text` given a `profile` and returns a list of tokens.
    """
    # We simply use the qalsadi lib to tokenize the text and then lemmatize and pos tag each word.
    # optionally use araby.tokenize_with_location
    raw_tokens = analex.text_tokenize(text)
    # analyzed has a list of possible configurations for each word.
    analyzed = analex.check_text(text)
    stemnodelist = lemmatizer.analyze(analyzed)
    lemmas = lemmatizer.get_lemmas(stemnodelist, return_pos=True)
    tokens = [
        Token(arab, lemma, pos, is_pausa=profile.pausa)
        for (arab, (lemma, pos)) in zip(raw_tokens, lemmas)
    ]
    tokens[-1].is_pausa = True
    # TODO: set is_part_of_idafah

    return tokens


def transliterate(text: str, profile: Profile) -> str:
    if not text:
        return ""
    tokens = tokenize(text, profile)
    for token in tokens:
        token.map_chars()
        token.determine_prefix()
        token.capitalize()
        token.assimilate()
    print(tokens)
    return " ".join(t.result() for t in tokens)


if __name__ == "__main__":
    text = "يَكْتُبُ الكَلْبُ"
    # text = "ﷲ"

    # print([hex(ord(x)) for x in text])

    profile = Profile(pausa=False)

    print(transliterate(text, profile))
