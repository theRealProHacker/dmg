from trans import transliterate, Profile


def test_sun_assimilation():
    # https://de.wikipedia.org/wiki/Sonnenbuchstabe
    tests = {"التَعلِيم": "at-taʿlīm", "الثَورَة": "aṯ-ṯawra"}
    profile = Profile()
    for arab, latin in tests.items():
        assert transliterate(arab, profile) == latin


test_sun_assimilation()
