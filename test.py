from trans import Profile, ner_available, transliterate

profile_pausa = Profile(pausa=True)


def test_tokenization():
    ...
    # TODO: find difficult edge cases


def test_transliteration_robustness():
    assert transliterate("") == ""
    assert transliterate(" ") == ""
    assert transliterate("?") == "?"
    assert transliterate("؟") == "?"
    assert transliterate("؟ \n") == "?"
    assert transliterate("أَ") in ("ʾ", "a")
    assert transliterate("آ") == "ā"
    assert transliterate("ذَهَبَ إِ") in ("ḏahaba ʾ", "ḏahaba i")


def test_half_vowels():
    assert transliterate("و") == "w"
    assert transliterate("شو") == "šū"
    assert transliterate("شَو") == "šaw"
    assert transliterate("شُو") == "šū"
    assert transliterate("شوك") == "šūk"


def test_sun_assimilation():
    # https://de.wikipedia.org/wiki/Sonnenbuchstabe
    no_diphthong_tests = {
        "التَعلِيم": "at-taʿlīm",
        "الثَورَة": "aṯ-ṯawra",
        "الدَولَة": "ad-dawla",
        "الذَرَّة": "aḏ-ḏarra",
        # "الرَإِيس": "ar-raʾīs",  # doesn't work, rais is not recognized
        "الزَيت": "az-zayt",
        # "السُكَّر": "as-sukkar",
        "الشَمس": "aš-šams",
        # "الصُندُق": "aṣ-ṣundūq",  # doesn't work, sunduq is not recognized
        "الضَيف": "aḍ-ḍayf",
        # "الطَاوِيلَة": "aṭ-ṭāwila",  # tawila is not recognized
        # "الظُهر": "aẓ-ẓuhr",
        "اللُغَة": "al-luġa",
        "النَوم": "an-nawm",
    }
    diphthong_tests = {
        "الدَولَة": "ad-daula",
        "الزَيت": "az-zait",
        "الضَيف": "aḍ-ḍaif",
        "النَوم": "an-naum",
    }
    for arab, latin in no_diphthong_tests.items():
        assert transliterate(arab) == latin

    for arab, latin in diphthong_tests.items():
        assert transliterate(arab, Profile(diphthongs=True)) == latin


def test_ta_marbutah():
    global profile_pausa
    profile_tm = Profile(ta_marbutah=True)
    profile_pausa_tm = Profile(pausa=True, ta_marbutah=True)
    assert transliterate("المَدِينَة") == "al-madīna"
    assert transliterate("المَدِينَة", profile_tm) == "al-madīnah"
    # assert transliterate("الشجرة في الحديقة كبيرة") == "aš-šaǧaratu fī l-ḥadīqati kabīratun."
    if ner_available:
        assert transliterate("مَدِينَةُ القَاهِرَةِ") == "madīnatu l-Qāhira"
        assert transliterate("مَدِينَةُ القَاهِرَةِ", profile_pausa) == "madīnat al-Qāhira"
        assert transliterate("مَدِينَةُ القَاهِرَةِ", profile_tm) == "madīnatu l-Qāhirah"
        assert transliterate("مَدِينَةُ القَاهِرَةِ", profile_pausa_tm) == "madīnat al-Qāhirah"
    assert transliterate("صَلاة") == "ṣalāh"


def test_diphthong():
    profile = Profile(diphthongs=True)
    # bayt
    assert transliterate("بَيت") == "bayt"
    assert transliterate("بَيت", profile) == "bait"
    # dawl
    assert transliterate("دَول") == "dawl"
    assert transliterate("دَول", profile) == "daul"
    # awwal
    assert transliterate("أَوَّل") == "awwal"
    assert transliterate("أَوَّل", profile) == "auwal"


def test_double_vowels():
    profile_double_vowels = Profile(double_vowels=False)
    # quwwah
    assert transliterate("قُوَّة") == "quwwa"
    assert transliterate("قُوَّة", profile_double_vowels) == "qūwa"
    # niyyah
    assert transliterate("نِيَّة") == "niyya"
    assert transliterate("نِيَّة", profile_double_vowels) == "nīya"



def test_hamzatul_wasl():
    assert transliterate("ابن") == "ibn"
    assert transliterate("اسم") == "ism"
    # assert transliterate("الَّذينَ") == "allaḏīna"
    assert transliterate("اِنْكَسَرَ") == "inkasara"
    assert transliterate("انْكَسَرَ") == "inkasara"
    # assert transliterate("ٱِنْكَسَرَ") == "inkasara"
    assert transliterate("الشَّاشَةُ اِنْكَسَرَتْ", profile_pausa) == "aš-šāša inkasarat"
    # assert transliterate("هَذَا احْتِمَالٌ عَظِيمٌ", profile_pausa) == "haḏā iḥtimāl ʿaẓīm"

    assert transliterate("الْمَكْتَبَةُ الْكَبِيرَةُ") == "al-maktabatu l-kabīra"


if ner_available:

    def test_names():
        assert transliterate("مُحَمَّد") == "Muḥammad"

    def test_allah():
        allah_forms = {
            # "ﷲ": "Allah",
            # billah
            # lillah
            # "ﺑﺴﻢ ﷲ": ""
        }
        for arab, latin in allah_forms.items():
            assert transliterate(arab) == latin


def test_prepositions():
    assert transliterate("فِي") == "fī"
    # assert transliterate("للامتحان") == "lil-imtiḥān"
    assert transliterate("كَتَبَ كَمُعَلِّم") == "kataba ka-muʿallim"


def test_ibrahim_text():
    p = Profile(pausa=True, double_vowels=False)
    with open("data/ibrahim-in.txt", encoding="utf-8") as inp, open("data/ibrahim-out.txt", encoding="utf-8") as outp:
        arab = "\n".join(line for line in inp.readlines() if not line.startswith("#"))
        latin = "\n".join(line for line in outp.readlines() if not line.startswith("#"))
        assert transliterate(arab, p) == latin.strip()

    # Still errors:
    # It's acually wan-niṣf, not wālniṣf
    # Ibrahim is not capitalized

    assert transliterate("براون آند كو", Profile(diphthongs=True)) == "brāun ānd kū"


if __name__ == "__main__":
    # test_prepositions()
    # test_transliteration_robustness()
    test_ibrahim_text()
    # test_hamzatul_wasl()
