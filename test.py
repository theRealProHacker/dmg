from pytest import main

from trans import Profile, ner_available, transliterate


def test_tokenization():
    ...
    # TODO: find difficult edge cases


def test_transliteration_safety():
    assert transliterate("") == ""
    assert transliterate(" ") == ""
    assert transliterate("?") == "?"
    assert transliterate("؟") == "?"
    assert transliterate("؟ \n") == "?"
    assert transliterate("أَ") == "a"  # ? what should this be ?
    assert transliterate("ذَهَبَ إِ") == "ḏahaba i"


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
        # "الرَإِيس": "ar-raʾīs",  # doesn't work, rais is not recognized
        "الزَيت": "az-zayt",
        "السُكَّر": "as-sukkar",
        "الشَمس": "aš-šams",
        # "الصُندُق": "aṣ-ṣundūq",  # doesn't work, sunduq is not recognized
        "الضَيف": "aḍ-ḍayf",  # daif
        # "الطَاوِيلَة": "aṭ-ṭāwila",  # tawila is not recognized
        "الظُهر": "aẓ-ẓuhr",
        "اللُغَة": "al-luġa",
        "النَوم": "an-nawm",  # naum
    }
    diphthong_tests = {
        "الدَولَة": "ad-daula",
        "الزَيت": "az-zait",
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
    if ner_available:
        assert transliterate("المَدِينَةُ القَاهِرَةِ", profile) == "al-madīnatu l-Qāhira"
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
    assert transliterate("بَيتُ") == "bayt"
    assert transliterate("بَيتُ", profile) == "bait"
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
    assert transliterate("ابن") == "ibn"
    assert transliterate("اسم") == "ism"
    assert transliterate("امرأة") == "imraʾa"
    assert transliterate("الَّذينَ") == "allaḏīna"


if ner_available:

    def test_names():
        assert transliterate("مُحَمَّد") == "Muḥammad"
        assert transliterate("اللَّه") == "Allāh"


def test_prepositions():
    assert transliterate("فِي") == "fī"
    # assert transliterate("للامتحان") == "lil-imtiḥān"
    assert transliterate("كَتَبَ كَمُعَلِّم") == "kataba ka-muʿallim"


def test_ibrahim_text():
    assert (
        transliterate("وَظِيفَةُ خَالِيَّةُ", Profile(pausa=True, double_vowels=False))
        == "waẓīfa ḫālīya"
    )

    assert (
        transliterate(
            "وَصَلَ إِبراهيم أِلَى الْمَكْتَبَ فِي السَّاعَةِ التَّاسِعَةِ وَالنِصف فَطَرَدَهُ المُدير۔",
            profile=Profile(pausa=True, double_vowels=False),
        )
        == "waṣala ibrāhīm ilā l-maktab fī s-sāʿat at-tāsiʿa wan-niṣf fa-ṭaradahu l-mudīr."
    )

    # assert

if __name__ == "__main__":
    main()