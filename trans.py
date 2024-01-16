from dataclasses import dataclass
import re
import data

@dataclass
class Profile:
    pausa: bool = False
    """Whether the text is in Pausa"""
    skip_final_h: bool = False
    """Whether a final h should be skipped"""
    skip_i3rab: bool = False
    """Whether i3rab (flexion endings) should be skipped"""
    full_vocalisation: bool = False
    """ Full vocalised transcription"""
    # TODO: Diphtonge: aw -> au
    # TODO: Zwei Doppelpunkte bei emphatischen Konsonanten
    # TODO: alif maqsura mit Unterpunkt
    # TODO: niyyah -> nīyah, awwal -> auwal
    # TODO: imalah, ishmam
    # TODO: alif maqsura to ya




@dataclass
class Token:
    arab: str
    pausa: bool = False
    latin: str = ""
    prefix: str = ""
    is_name: bool = False

    def determine_prefix(self):
        """
        Determines whether the token begins with a prefix 
        and sets the prefix attribute accordingly
        """
        if self.latin in data.prefix_blacklist:
            return
        for length in data.prefix_lengths:
            # TODO: check if this works for small words
            if self.latin[:length] in data.prefixes:
                self.prefix = self.latin[:length]
                self.latin = self.latin[length:]
                break

    def map_chars(self):
        """
        Replaces the arab chars with latin chars
        and sets the latin attribute accordingly
        """
        char_map = data.subs|data.diacritic_map|data.char_map|data.special_char_map
        if self.pausa:
            char_map = data.pausa_map | char_map | data.pausa_map
        rules = [
            (re.compile(arab), latin) for arab, latin in char_map.items()
        ]
        word = self.arab
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
        self.is_name = self.latin in data.proper_names

    def assimilate(self):
        """
        Apply internal assimilations to the latin 
        """
        # sun letter assimilation
        first_letter = self.latin[0]
        if self.prefix.endswith("al") and first_letter in data.sun_letters:
            self.prefix = self.prefix[:-1]+first_letter

    def result(self):
        """
        Returns the transliterated word
        """
        if self.is_name:
            self.latin = self.latin.capitalize()
        return (self.prefix+"-" if self.prefix else "") + self.latin

def tokenize(text: str, profile: Profile)->list[Token]:
    tokens = [
        Token(w, pausa=profile.pausa) for w in text.split()
    ]
    tokens[-1].pausa = True
    return tokens

def transliterate(text: str, profile: Profile)->str:
    tokens = tokenize(text, profile)
    print(tokens)
    for token in tokens:
        token.map_chars()
        token.determine_prefix()
        token.capitalize()
        token.assimilate()
    print(tokens)
    return " ".join(t.result() for t in tokens)

if __name__ == "__main__":
    text = "يَكتُب أَلْكَلْب"
    # text = "ﷲ"

    # print([hex(ord(x)) for x in text])

    profile = Profile(pausa=False)

    print(transliterate(text, profile))