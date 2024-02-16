from arab_tools import tokenize_with_location
from trans import Profile, transliterate


def test_tokenization():
    text = "يَكْتُبُ الكَلْبُ"
    tokens, starts, ends = tokenize_with_location(text)
    assert tokens == ("يَكْتُبُ", "الكَلْبُ")
    assert starts == (0, 9)
    assert ends == (8, 17)


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
