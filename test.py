import arab_tools
import data
from data_types import IJMESProfile, NameProfile
from trans import Profile, transliterate, transliterate_ijmes

profile_pausa = Profile(pausa=True)


def test_separate_join():
    assert arab_tools.separate("مَدِينَة") == (
        ["م", "د", "ي", "ن", "ة"],
        [data.fatha, data.kasra, "", data.fatha, ""],
    )
    assert (
        arab_tools.join(
            ["م", "د", "ي", "ن", "ة"], [data.fatha, data.kasra, "", data.fatha, ""]
        )
        == "مَدِينَة"
    )
    # muhammad
    muhammad = "مُحَمَّد"
    assert muhammad == arab_tools.join(
        *arab_tools.separate(muhammad)
    ), arab_tools.separate(muhammad)
    assert arab_tools.inject("ا", "الله", 3) == "اللاه"
    rasm, harakat = arab_tools.separate("أَنا")
    rasm.pop(-1)
    harakat.pop(-1)
    harakat[-1] = data.fatha
    assert arab_tools.join(rasm, harakat) == "أَنَ"


def test_transliteration_robustness():
    assert transliterate("") == ""
    assert transliterate(" ") == ""
    assert transliterate("?") == "?"
    assert transliterate("؟") == "?"
    assert transliterate("؟ \n") == "?"
    assert transliterate("١٤") == "14"
    assert transliterate("أَ") in ("ʾ", "a")
    assert transliterate("آ") == "ā"
    assert transliterate("ذَهَبَ إِ") in ("ḏahaba ʾ", "ḏahaba i")
    assert transliterate(" َكبَر") == "akbar"


def test_alif():
    assert transliterate("قُرآن") == "qurʾān"


def test_half_vowels():
    assert transliterate("و") == "w"
    assert transliterate("شو") == "šū"
    assert transliterate("شَو") == "šaw"
    assert transliterate("شُو") == "šū"
    assert transliterate("شوك") == "šūk"


def test_prefixes():
    # sa
    # assert transliterate("سَأَكون")
    # lil
    assert transliterate("للامتِحان") == "li-l-imtiḥān"
    # ka
    assert transliterate("كَتَبَ كَمُعَلِّم") == "kataba ka-muʿallim"
    assert transliterate("كاليَوم") == "ka-l-yawm"
    # bil
    assert transliterate("بِالْبَيت") == "bi-l-bayt"
    # wa-lil
    assert transliterate("وَلِالاستِشراق") == "wa-li-l-istišrāq"


def test_sun_assimilation():
    # https://de.wikipedia.org/wiki/Sonnenbuchstabe
    no_diphthong_tests = {
        "التَعلِيم": "at-taʿlīm",
        "الثَورَة": "aṯ-ṯawra",
        "الدَولَة": "ad-dawla",
        "الذَرَّة": "aḏ-ḏarra",
        "الرَئيس": "ar-raʾīs",
        "الزَيت": "az-zayt",
        "السُكَّر": "as-sukkar",
        "الشَمس": "aš-šams",
        # "الصُندُق": "aṣ-ṣundūq",  # doesn't work, sunduq is not recognized
        "الضَيف": "aḍ-ḍayf",
        # "الطَاوِيلَة": "aṭ-ṭāwila",  # tawila is not recognized
        "الظُهر": "aẓ-ẓuhr",
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
    assert (
        transliterate("الشَجَرَةُ في الحَديقَةِ كَبيرَةٌ")
        == "aš-šaǧaratu fī l-ḥadīqati kabīratun"
    )
    assert transliterate("مَدِينَةُ القَاهِرَةِ") == "madīnatu l-qāhirati"
    assert transliterate("مَدِينَةُ القَاهِرَةِ", profile_pausa) == "madīnat al-qāhira"
    assert transliterate("مَدِينَةُ القَاهِرَةِ", profile_tm) == "madīnatu l-qāhirati"
    assert transliterate("مَدِينَةُ القَاهِرَةِ", profile_pausa_tm) == "madīnat al-qāhirah"
    assert transliterate("صَلاة") == "ṣalāh"
    assert transliterate("ﻣِﺮﺁة") == "mirʾāh"


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
    assert transliterate("ابنُ") == "ibnu"
    assert transliterate("اسم") == "ism"
    assert transliterate("اسمُ") == "ismu"
    assert transliterate("الَّذينَ") == "allaḏīna"
    assert transliterate("اِنْكَسَرَ") == "inkasara"
    assert transliterate("انْكَسَرَ") == "inkasara"
    assert transliterate("ٱِنْكَسَرَ") == "inkasara"
    assert transliterate("اسْتِشْرَاق") == "istišrāq"
    assert transliterate("فَانتَقَلَ") == "fa-ntaqala"  # with prefix
    assert transliterate("اخرُج") == "uḫruǧ"
    assert transliterate("هُم الكُتّاب") == "hum ul-kuttāb"
    assert transliterate("عَن الْكِتابُ", profile_pausa) == "ʿan il-kitāb"
    assert transliterate("مِنْ البَيت") == "min al-bayt"

    # this looks like it ends in a vowel, but it doesn't
    assert transliterate("الشَّاشَةُ اِنْكَسَرَتْ", profile_pausa) == "aš-šāša inkasarat"
    assert transliterate("هَذَا احْتِمَالٌ عَظِيمٌ", profile_pausa) == "hāḏā ḥtimāl ʿaẓīm"

    assert transliterate("الْمَكْتَبَةُ الْكَبِيرَةُ") == "al-maktabatu l-kabīratu"

    assert transliterate("الجُندِيّ العَرَبِيّ") == "al-ǧundī al-ʿarabī"
    assert transliterate("ﻓﻲ اﻟﺒَﻴﺖ") == "fī l-bayt"


def test_pronouns_and_prepositions():
    assert transliterate("أَنْتَ") == "anta"
    assert transliterate("أَنْتِ") == "anti"
    assert transliterate("هُوَ") == "huwa"
    assert transliterate("هِيَ") == "hiya"
    assert transliterate("نَحْنُ") == "naḥnu"
    assert transliterate("أَنْتُمْ") == "antum"
    assert transliterate("هُمْ") == "hum"
    assert transliterate("هُنَّ") == "hunna"
    assert transliterate("لِي") == "lī"
    assert transliterate("لَكَ") == "laka"
    assert transliterate("لَكِ") == "laki"
    assert transliterate("لَهُ") == "lahu"
    assert transliterate("لَهَا") == "lahā"
    assert transliterate("لَنَا") == "lanā"
    assert transliterate("لَكُم") == "lakum"
    assert transliterate("لَهُم") == "lahum"
    assert transliterate("لَهُنَّ") == "lahunna"


def test_endings():
    # shukran und taqriban
    assert transliterate("شُكْرًا", profile_pausa) == "šukran"
    assert transliterate("تَقْرِيباً", profile_pausa) == "taqrīban"

    # waw + alif -> waw
    assert transliterate("ﻗﺎﻟﻮا") == "qālū"
    assert transliterate("رَأَوا") == "raʾaw"
    assert transliterate("رَأَوا", Profile(diphthongs=True)) == "raʾau"


def test_nisba():
    # nabi
    assert transliterate("نَبِيٌّ", profile_pausa) == "nabī"
    assert transliterate("نَبِيٌّ", Profile(pausa=True, double_vowels=False)) == "nabī"
    assert transliterate("نَبِيٌّ", Profile(pausa=True, nisba=False)) == "nabiyy"
    assert (
        transliterate("نَبِيٌّ", Profile(pausa=True, nisba=False, double_vowels=False))
        == "nabīy"
    )
    # al-arabi
    assert transliterate("العَرَبِيّ", profile_pausa) == "al-ʿarabī"
    assert (
        transliterate("العَرَبِيّ", Profile(pausa=True, double_vowels=False)) == "al-ʿarabī"
    )
    assert transliterate("العَرَبِيّ", Profile(pausa=True, nisba=False)) == "al-ʿarabī"
    assert (
        transliterate("العَرَبِيّ", Profile(pausa=True, nisba=False, double_vowels=False))
        == "al-ʿarabī"
    )


def test_hu_hi():
    # abuhu
    assert transliterate("لِأَبُوهُ") == "li-abūhu"
    assert transliterate("لِأَبُوهُ", Profile(hu_hi=False)) == "li-abūhu"
    # baytuhu
    assert transliterate("بَيْتُهُ") == "baytuhū"
    assert transliterate("بَيْتُهُ", Profile(hu_hi=False)) == "baytuhu"
    # dhahaba ilayhi
    assert transliterate("ذَهَبَ إِلَيْهِ", Profile(hu_hi=False)) == "ḏahaba ilayhi"
    assert transliterate("ذَهَبَ إِلَيْهِ") == "ḏahaba ilayhi"


def test_special_words():
    # Allah
    assert transliterate("ﷲ") == "Allāh"  # ligature
    assert transliterate("الله") == "Allāh"
    assert transliterate("والله") == "wa-llāh"
    assert transliterate("لله", profile_pausa) == "li-llāh"
    assert transliterate("عَبد الله") == "ʿabd Allāh"
    assert transliterate("عَبدُ الله") == "ʿabdu llāh"
    assert transliterate("هُم الله") == "hum ullāh"
    # ilah
    assert transliterate("إِلَه") == "ilāh"
    # rahman
    assert transliterate("رَحْمَن") == "raḥmān"
    # ana
    assert transliterate("أَنَا") == "ana"
    # hadha
    assert transliterate("هَذَا") == "hāḏā"
    assert transliterate("هَذِهِ") == "hāḏihi"
    # dhalika
    assert transliterate("ذَلِكَ") == "ḏālika"
    assert transliterate("كَذَلِكَ") == "kaḏālika"
    # hakadha
    assert transliterate("هَكَذَا") == "hākaḏā"
    # lakin
    assert transliterate("لَكِن") == "lākin"
    assert transliterate("لَكِنَّ") == "lākinna"
    # ulaika
    assert transliterate("أُولَئِكَ") == "ulāʾika"
    assert transliterate("أُولَٰئِكَ") == "ulāʾika"
    # Taha
    assert transliterate("طَهَ") == "ṭāhā"
    # Ibrahim
    assert transliterate("إِبْرَاهِيم") == "ibrāhīm"
    # Amr
    assert transliterate("عَمرَو") == "ʿamr"


def _test_ibrahim_text():
    p = Profile(pausa=True, double_vowels=False)
    with open("data/ibrahim-in.txt", encoding="utf-8") as inp, open(
        "data/ibrahim-out.txt", encoding="utf-8"
    ) as outp:
        arab = "\n".join(line for line in inp.readlines() if not line.startswith("#"))
        latin = "\n".join(line for line in outp.readlines() if not line.startswith("#"))
        assert transliterate(arab, p) == latin.strip()

    # Still errors:
    # It's acually wan-niṣf, not wālniṣf
    # Ibrahim is not capitalized

    assert transliterate("براون آند كو", Profile(diphthongs=True)) == "brāun ānd kū"


def test_names():
    tests = {
        # "عَيْنُ التَّابْغَةِ": "ʿAyn at-Tābġa",
        "النِّيلُ": "an-Nīl",
        "ابْنُ بَطّوطَةَ": "Ibn Baṭṭūṭa",
        "أَبُو عَبْدِ الله مُحَمَّدٌ ابْنُ بَطّوطَةَ": "Abū ʿAbdallāh Muḥammad b. Baṭṭūṭa",
        "أَبو حامِد مُحَمَّد الغَزّالِي": "Abū Ḥāmid Muḥammad al-Ġazzālī",
        "كِتاب الأَغاني لِلإِمام أَبي الفَرَج": "Kitāb al-Aġānī li-l-Imām Abī l-Faraǧ",
    }
    for arab, latin in tests.items():
        assert transliterate(arab, NameProfile()) == latin

    assert transliterate("أَبُو بَكْر", NameProfile()) == "Abū Bakr"
    assert (
        transliterate(
            "أَبُو عَبْدِ الله مُحَمَّدٌ ابْنُ بَطّوطَةَ", profile=NameProfile(short_ibn=False)
        )
        == "Abū ʿAbdallāh Muḥammad ibn Baṭṭūṭa"
    )
    assert (
        transliterate("ابْنُ بَطّوطَةَ", profile=NameProfile(short_ibn=True)) == "Ibn Baṭṭūṭa"
    )

    assert (
        transliterate(
            "كِتاب الأَغاني لِلإِمام أَبي الفَرَج", profile=NameProfile(is_book=True)
        )
        == "Kitāb al-Aġānī li-l-imām abī l-faraǧ"
    )


def test_ijmes():
    name_profile = IJMESProfile(is_name=True)

    assert transliterate_ijmes("ثَورَة ١٤ تَمّوز") == "thawra 14 tammūz"
    # Doesn't detect idafah with the number
    assert transliterate_ijmes("ثَورَة ١٤ تَمّوز") != "thawrat 14 tammūz"
    # Detects idafah without number
    assert transliterate_ijmes("مَكتَبَةُ الجامِعَةِ") != "maktabat al-gāmiʿa"

    assert (
        transliterate_ijmes("الإِخوَان المُسلِمون", name_profile) == "al-Ikhwan al-Muslimun"
    )
    assert (
        transliterate_ijmes("فَيْسَل التَفْرِيقَة بَين الإِسلَام وَالزَنْدَقَة", name_profile)
        == "Faysal al-Tafriqa bayn al-Islam wa-l-Zandaqa"
    )
    assert (
        transliterate_ijmes("النور أَخبَر القَرن العَشير", name_profile)
        == "al-Nur Akhbar al-Qarn al-ʿAshir"
    )
    # doesn't recognize Safirʿan
    assert (
        transliterate_ijmes("النور السَافِرْعَن أَخبَر القَرن العَشير", name_profile)
        != "al-Nur al-Safirʿan Akhbar al-Qarn al-ʿAshir"
    )

    assert transliterate_ijmes("في العِراق وَمِصر", name_profile) == "fi al-ʿIraq wa-Misr"
    assert transliterate_ijmes("في مِصر وَالعِراق") == "fī miṣr wa-l-ʿirāq"

    assert transliterate_ijmes("مِصرِيّ") == "miṣriyya"
    assert transliterate_ijmes("نَبِيٌّ") == "nabī"

    assert transliterate_ijmes("عَلِيّ ابن أَبي طَالِب", name_profile) == "ʿAli ibn Abi Talib"
    assert transliterate_ijmes("أُسَامَة بِن لادِن", name_profile) == "Usama bin Ladin"
    assert transliterate_ijmes("بِن لادِن", name_profile) == "Bin Ladin"

    assert transliterate_ijmes("الله", name_profile) == "Allah"


if __name__ == "__main__":
    # test_prepositions()
    # test_transliteration_robustness()
    # test_ibrahim_text()
    # test_hamzatul_wasl()
    print(transliterate("اسْتِشْرَاقٌ"))
