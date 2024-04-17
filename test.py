from pytest import main

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
    assert transliterate("أَ") == "ʾ"
    assert transliterate("آ") == "ā"
    assert transliterate("ذَهَبَ إِ") == "ḏahaba ʾ"


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
        assert transliterate("المَدِينَةُ القَاهِرَةِ") == "al-madīnatu l-Qāhira"
        assert transliterate("المَدِينَةُ القَاهِرَةِ", profile_pausa) == "al-madīnat al-Qāhira"
        assert transliterate("المَدِينَةُ القَاهِرَةِ", profile_tm) == "al-madīnatu l-Qāhirah"
        assert (
            transliterate("المَدِينَةُ القَاهِرَةِ", profile_pausa_tm)
            == "al-madīnat al-Qāhirah"
        )
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
    profile = Profile(double_vowels=False)
    # quwwah
    assert transliterate("قُوَّة") == "quwwa"
    assert transliterate("قُوَّة", profile) == "qūwa"
    # niyyah
    assert transliterate("نِيَّة") == "niyya"
    assert transliterate("نِيَّة", profile) == "nīya"


def test_hamzatul_wasl():
    assert transliterate("ابن") == "ibn"
    assert transliterate("اسم") == "ism"
    assert transliterate("الَّذينَ") == "allaḏīna"
    assert transliterate("اِنْكَسَرَ") == "inkasara"
    assert transliterate("انْكَسَرَ") == "inkasara"
    assert transliterate("ٱِنْكَسَرَ") == "inkasara"
    assert transliterate("الشَّاشَةُ اِنْكَسَرَتْ", profile_pausa) == "aš-šāša nkasarat"
    assert transliterate("هَذَا احْتِمَالٌ عَظِيمٌ", profile_pausa) == "haḏā iḥtimāl ʿaẓīm"

    assert transliterate("الْمَكْتَبَةُ الْكَبِيرَةُ") == "al-maktaba l-kabīra"


if ner_available:

    def test_names():
        assert transliterate("مُحَمَّد") == "Muḥammad"
        assert transliterate("اللَّه") == "Allāh"


def test_prepositions():
    assert transliterate("فِي") == "fī"
    # assert transliterate("للامتحان") == "lil-imtiḥān"
    assert transliterate("كَتَبَ كَمُعَلِّم") == "kataba ka-muʿallim"


def test_ibrahim_text():
    # A more general test that includes all kind of features

    assert (
        transliterate("وَظِيفَةُ خَالِيَّةُ", Profile(pausa=True, double_vowels=False))
        == "waẓīfa ḫālīya"
    )

    # It's acually wan-niṣf, not wālniṣf
    assert (
        transliterate(
            "وَصَلَ إِبراهيم أِلَى الْمَكْتَبَ فِي السَّاعَةِ التَّاسِعَةِ وَالنِصف فَطَرَدَهُ المُدير۔",
            profile=Profile(pausa=True, double_vowels=False),
        )
        == "waṣala ibrāhīm ilā l-maktab fī s-sāʿat at-tāsiʿa wālniṣf fa-ṭaradahu l-mudīr."
    )

    assert (
        transliterate(
            "ذَهَبَ إِبراهيم إِلى مَكتَبِ العَمَلِ وَطَلَبَ وَظيفَةَ خالِيَّةِ فَقالَ لَهُ المُوَظَّف۔",
            profile=Profile(double_vowels=False),
        )
        == "ḏahaba ibrāhīm ilā maktabi l-ʿamali wa-ṭalaba waẓīfata ḫālīyati fa-qāla lahu l-muwaẓẓaf."
    )

    assert (
        transliterate(
            "هُناكَ وَظيفَة خَلِيَّة في شَرِكَة تَأمين",
            profile=Profile(double_vowels=False),
        )
        == "hunāka waẓīfa ḫalīya fī šarika taʾmīn"
    )

    assert transliterate("براون آند كو") == "brāun ānd kū"


if __name__ == "__main__":
    main()
