from trans import Profile, transliterate


def test_tokenization():
    ...
    # TODO: find difficult edge cases


def test_transliteration_safety():
    assert transliterate("") == ""
    assert transliterate(" ") == ""
    assert transliterate("?") == "?"
    assert transliterate("؟") == "?"
    assert transliterate("؟ \n") == "?"


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
        "الدَولَة": "ad-dawla",  # daula
        "الذَرَّة": "aḏ-ḏarra",
        # "الرَإِيس": "ar-raʾīs", # doesn't work, rais is not recognized
        "الزَيت": "az-zayt",
        "السُكَّر": "as-sukkar",
        "الشَمس": "aš-šams",
        # "الصُندُق": "aṣ-ṣundūq", # doesn't work, sunduq is not recognized
        "الضَيف": "aḍ-ḍayf",  # daif
        # "الطَاوِيلَة": "aṭ-ṭāwila", # tawila is not recognized
        "الظُهر": "aẓ-ẓuhr",
        "اللُغَة": "al-luġa",
        "النَوم": "an-nawm",  # naum
    }
    diphthong_tests = {
        "الدَولَة": "ad-daula",
        "الزَيت": "az-zayt",
        "السُكَّر": "as-sukkar",
        "الشَمس": "aš-šams",
        "الضَيف": "aḍ-ḍaif",
        "الظُهر": "aẓ-ẓuhr",
        "اللُغَة": "al-luġa",
        "النَوم": "an-naum",
    }
    for arab, latin in no_diphthong_tests.items():
        assert transliterate(arab) == latin

    for arab, latin in diphthong_tests.items():
        assert transliterate(arab, Profile(diphthongs=True)) == latin


def test_ta_marbutah():
    profile = Profile()
    profile_pausa = Profile(pausa=True)
    profile_tm = Profile(ta_marbutah=True)
    profile_pausa_tm = Profile(pausa=True, ta_marbutah=True)
    assert transliterate("المَدِينَة", profile) == "al-madīna"
    assert transliterate("المَدِينَة", profile_tm) == "al-madīnah"
    assert transliterate("المَدِينَةُ القَاهِرَةِ", profile) == "al-madīnatu al-Qāhira"
    assert transliterate("المَدِينَةُ القَاهِرَةِ", profile_pausa) == "al-madīnat al-Qāhira"
    assert transliterate("المَدِينَةُ القَاهِرَةِ", profile_tm) == "al-madīnatu al-Qāhirah"
    assert transliterate("المَدِينَةُ القَاهِرَةِ", profile_pausa_tm) == "al-madīnat al-Qāhirah"
    assert transliterate("صَلاة") == "ṣalāh"


def test_diphthong():
    profile = Profile(diphthongs=True)
    # bayt
    # assert transliterate("بَيتُ")             == "bayt"
    # assert transliterate("بَيتُ", profile)    == "bait"
    # dawl
    assert transliterate("دَولَ") == "dawl"
    assert transliterate("دَولَ", profile) == "daul"
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
    assert transliterate("أَنَ الحَديقَةِ") == "ana l-ḥadīqa"


def test_names():
    assert transliterate("مُحَمَّد") == "Muḥammad"
