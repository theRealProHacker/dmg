from arab_tools import tokenize_with_location
from trans import Profile, transliterate


def test_tokenization():
    text = "يَكْتُبُ الكَلْبُ"
    tokens, starts, ends = tokenize_with_location(text)
    assert tokens == ("يَكْتُبُ", "الكَلْبُ")
    assert starts == (0, 9)
    assert ends == (8, 17)

    # TODO: find more difficult edge cases

def test_transliteration_safety():
    assert transliterate("") == ""
    assert transliterate(" ") == ""
    assert transliterate("?") == "?"
    assert transliterate("؟") == "?"
    assert transliterate("؟ \n") == "?"

def test_sun_assimilation():
    # https://de.wikipedia.org/wiki/Sonnenbuchstabe
    tests = {
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
    profile = Profile()
    for arab, latin in tests.items():
        assert transliterate(arab, profile) == latin

def test_ta_marbutah():
    profile = Profile()
    profile_pausa = Profile(pausa=True)
    profile_ta_marbutah = Profile(ta_marbutah=True)
    profile_pausa_ta_marbutah = Profile(pausa=True, ta_marbutah=True)
    assert transliterate("المَدِينَة", profile) == "al-madīna"
    assert transliterate("المَدِينَة", profile_ta_marbutah) == "al-madīnah"
    # al-Qāhirah
    assert transliterate("المَدِينَةُ القَاهِرَةِ", profile) == "al-madīnatu al-qāhira"
    # assert transliterate("المَدِينَةُ القَاهِرَةِ", profile_pausa) == "al-madīnat al-qāhira"
    assert transliterate("المَدِينَةُ القَاهِرَةِ", profile_ta_marbutah) == "al-madīnatu al-qāhirah"
    # assert transliterate("المَدِينَةُ القَاهِرَةِ", profile_pausa_ta_marbutah) == "al-madīnat al-qāhirah"
    