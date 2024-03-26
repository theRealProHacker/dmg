"""
This nounstemmer module is a port of the nounstemmer.py file from the qalsadi package.

This file is licensed under the GPLv3 license, and the original source code can be found at:

https://github.com/linuxscout/qalsadi/blob/master/qalsadi/stem_noun.py

"""

from functools import cache

import alyahmor.aly_stem_noun_const as SNC
import alyahmor.noun_affixer
import tashaphyne.stemming
from pyarabic import araby
from qalsadi.wordcase import WordCase

import data

comp_stemmer = tashaphyne.stemming.ArabicLightStemmer()
comp_stemmer.set_prefix_list(SNC.COMP_PREFIX_LIST)
comp_stemmer.set_suffix_list(SNC.COMP_SUFFIX_LIST)

conj_stemmer = tashaphyne.stemming.ArabicLightStemmer()
conj_stemmer.set_prefix_list(SNC.CONJ_PREFIX_LIST)
conj_stemmer.set_suffix_list(SNC.CONJ_SUFFIX_LIST)

generator = alyahmor.noun_affixer.noun_affixer()


def lookup_dict(word):
    return data.noun_dict.get(word, [])


def verify_affix(word, list_seg, affix_list):
    """
    Verify possible affixes in the resulted segments according
    to the given affixes list.
    @param word: the input word.
    @type word: unicode.
    @param list_seg: list of word segments indexes (numbers).
    @type list_seg: list of pairs.
    @return: list of acceped segments.
    @rtype: list of pairs.
    """
    return [s for s in list_seg if "-".join([word[: s[0]], word[s[1] :]]) in affix_list]


def stem_variants(stem, enclitic_nm):
    """generate stem variants"""
    list_stem = []
    if enclitic_nm:
        # حالة الاسم المقصور إذا كان به زيادة مثل سوى +ها = سواها
        if stem.endswith(araby.ALEF):
            list_stem.append(stem[:-1] + araby.ALEF_MAKSURA)
        # حالة المؤنث بالتاء قد يكون أصلها تاء مربوطة
        elif stem.endswith(araby.TEH):
            list_stem.append(stem[:-1] + araby.TEH_MARBUTA)
    # Case of Mankous Name حالة الاسم المنقوص
    # إذا لم يكن به زيادة ربما كان الاسم منقوصا منوّنا
    # قد يقبل السابقة مثل وقاضٍ
    # لكنه لا يقبل اللاحقة
    else:  # no enclitic
        list_stem.append(stem + araby.YEH)
    return list_stem


def noun_variants(noun: str) -> list[str]:
    noun_list = []
    if araby.ALEF_MADDA in noun:
        noun_list.append(noun.replace(araby.ALEF_MADDA, araby.ALEF_HAMZA_ABOVE * 2))
        noun_list.append(noun.replace(araby.ALEF_MADDA, araby.HAMZA + araby.ALEF))
        noun_list.append(
            noun.replace(araby.ALEF_MADDA, araby.ALEF_HAMZA_ABOVE + araby.ALEF)
        )
    return noun_list


def validate_tags(noun_tuple, affix_tags, proclitic, enclitic_nm, suffix_nm):
    """
    Test if the given word from dictionary is compabilbe with affixes tags.
    @param noun_tuple: the input word attributes given from dictionary.
    @type noun_tuple: dict.
    @param affix_tags: a list of tags given by affixes.
    @type affix_tags:list.
    @param proclitic_nm: first level prefix vocalized.
    @type proclitic_nm: unicode.
    @param enclitic_nm: first level suffix vocalized.
    @type enclitic_nm: unicode.
    @param suffix_nm: first level suffix vocalized.
    @type suffix_nm: unicode.
    @return: if the tags are compatible.
    @rtype: Boolean.
    """
    # ~ proclitic = araby.strip_tashkeel(proclitic)
    # ~ enclitic = enclitic_nm
    # ~ suffix = suffix_nm
    if "تنوين" in affix_tags and noun_tuple["mamnou3_sarf"]:
        return False
    # ألجمع السالم لا يتصل بجمع التكسير
    if noun_tuple["number"] in ("جمع", "جمع تكسير"):
        if "جمع مؤنث سالم" in affix_tags:
            return False
        if "جمع مذكر سالم" in affix_tags:
            return False
        if "مثنى" in affix_tags:
            return False
    # تدقيق الغضافة إلى الضمائر المتصلة
    if enclitic_nm in ("هم", "هن", "كما", "كم", "هما") and not noun_tuple["hm_suffix"]:
        return False
    if enclitic_nm in ("ه", "ها") and not noun_tuple["ha_suffix"]:
        return False
    # حالة قابلية السوابق  بدون تعريف
    if "ال" not in proclitic and not noun_tuple["k_prefix"]:
        return False
    # حالة قابلية السوابق  مع التعريف
    if proclitic.endswith("ال") and not noun_tuple["kal_prefix"]:
        return False
    # حالة المضاف إلى ما بعهده في حالة جمع المذكر السالم
    # مثل لاعبو، رياضيو
    if suffix_nm == araby.WAW and not noun_tuple["w_suffix"]:
        return False
    # التاء المربوطة لا تتصل بجمع التكسير
    if suffix_nm == araby.TEH_MARBUTA and noun_tuple["number"] == "جمع":
        return False
    # elif  u'مضاف' in affix_tags and not noun_tuple['annex']:
    # return False

    # todo
    # u'mankous':8,
    # u'feminable':9, *
    # u'number':10,
    # u'dualable':11, *
    # u'masculin_plural':12, *
    # u'feminin_plural':13, *
    # u'broken_plural':14,
    # u'mamnou3_sarf':15,
    # u'relative':16,
    # u'w_suffix':17,
    # u'hm_suffix':18, *
    # u'kal_prefix':19, *
    # u'ha_suffix':20, *
    # u'k_suffix':21, *
    # u'annex':22,
    return True


def get_stem_variants(stem: str, suffix_nm: str):
    """
    Generate the Noun stem variants according to the affixes.
    For example مدرستي => مدرست+ي => مدرسة + ي.
    Return a list of possible cases.
    @param stem: the input stem.
    @type stem: unicode.
    @param suffix_nm: suffix (no mark).
    @type suffix_nm: unicode.
    @return: list of stem variants.
    @rtype: list of unicode.
    """
    # some cases must have some correction
    # determinate the  suffix types
    # ~suffix = suffix_nm

    possible_noun_list = {stem}
    if suffix_nm in (
        araby.ALEF + araby.TEH,
        araby.YEH + araby.TEH_MARBUTA,
        araby.YEH,
        araby.YEH + araby.ALEF + araby.TEH,
    ):
        possible_noun = stem + araby.TEH_MARBUTA
        possible_noun_list.add(possible_noun)
    # فئت +ان
    if suffix_nm in (araby.ALEF + araby.NOON, araby.YEH + araby.NOON) and stem.endswith(
        araby.TEH
    ):
        possible_noun = stem[:-1] + araby.TEH_MARBUTA
        possible_noun_list.add(possible_noun)

    if not suffix_nm or suffix_nm in (araby.YEH + araby.NOON, araby.WAW + araby.NOON):
        possible_noun = stem + araby.YEH
        possible_noun_list.add(possible_noun)
    if stem.endswith(araby.YEH):
        # إذا كان أصل الياء ألفا مقصورة
        possible_noun = stem[:-1] + araby.ALEF_MAKSURA
        possible_noun_list.add(possible_noun)

    if stem.endswith(araby.HAMZA):
        possible_noun = stem[:-1] + araby.YEH_HAMZA
        possible_noun_list.add(possible_noun)
        # ~ possible_noun = stem[:-1] + araby.WAW_HAMZA
        # ~ possible_noun_list.add(possible_noun)
    # to be validated
    return [*possible_noun_list]


def is_valid_affix(proclitic_tags, enclitic_tags, suffix_tags) -> bool:
    if (
        "تعريف" in proclitic_tags
        and "مضاف" in suffix_tags
        and "مضاف" not in enclitic_tags
    ):
        return False
    elif "تعريف" in proclitic_tags and "تنوين" in suffix_tags:
        return False
    elif "تعريف" in proclitic_tags and "إضافة" in suffix_tags:
        return False
    elif "مضاف" in enclitic_tags and "تنوين" in suffix_tags:
        return False
    elif "مضاف" in enclitic_tags and "لايضاف" in suffix_tags:
        return False
    elif "جر" in proclitic_tags and "مجرور" not in suffix_tags:
        return False
    return True


def check_clitic_affix(noun_tuple, proclitic, enclitic, suffix):
    # avoid Fathatan on no ALEF Tawnwin expect on Teh marbuta and Alef followed by Hamza
    if suffix == araby.FATHATAN and not (
        noun_tuple["unvocalized"].endswith(araby.TEH_MARBUTA)
        or noun_tuple["unvocalized"].endswith(araby.ALEF + araby.HAMZA)
    ):
        return False
    # avoid masculin regular plural with unallowed case
    if (
        "جمع مذكر سالم" in SNC.CONJ_SUFFIX_LIST_TAGS[suffix]["tags"]
        and not noun_tuple["masculin_plural"]
    ):
        return False

    if (
        "تنوين" in SNC.CONJ_SUFFIX_LIST_TAGS[suffix]["tags"]
        and noun_tuple["mamnou3_sarf"]
    ):
        return False
    if not proclitic and not enclitic:
        return True

    # get proclitics and enclitics tags
    proclitic_tags = SNC.COMP_PREFIX_LIST_TAGS[proclitic]["tags"]
    enclitic_tags = SNC.COMP_SUFFIX_LIST_TAGS[enclitic]["tags"]
    # in nouns there is no prefix
    suffix_tags = SNC.CONJ_SUFFIX_LIST_TAGS[suffix]["tags"]
    # in some cases the suffixes have more cases
    # add this cases to suffix tags
    suffix_tags += SNC.CONJ_SUFFIX_LIST_TAGS[suffix].get("cases", ())
    return is_valid_affix(proclitic_tags, enclitic_tags, suffix_tags)


@cache
def vocalize(noun, proclitic, suffix, enclitic):
    """
    Vocalizes a noun.
    """
    return generator.vocalize(noun, proclitic, suffix, enclitic)


def stem_noun(noun: str) -> list[WordCase]:
    detailed_result = []
    noun_list = [*{noun, *noun_variants(noun)}]

    word_segmented_list = []
    for noun in noun_list:
        list_seg_comp = comp_stemmer.segment(noun)
        # filter
        list_seg_comp = verify_affix(noun, list_seg_comp, SNC.COMP_NOUN_AFFIXES)
        # treat multi vocalization enclitic
        for seg in list_seg_comp:
            proclitic_nm = noun[: seg[0]]
            stem = noun[seg[0] : seg[1]]
            enclitic_nm = noun[seg[1] :]
            # ajusting nouns variant
            list_stem = [
                stem,
            ] + stem_variants(stem, enclitic_nm)

            # stem reduced noun : level two
            for stem in list_stem:
                word_seg = {
                    "noun": noun,
                    "stem_comp": stem,
                    "pro": proclitic_nm,
                    "enc": enclitic_nm,
                }
                word_segmented_list.append(word_seg)

    # level two
    tmp_list = []

    for word_seg in word_segmented_list:
        list_seg_conj = conj_stemmer.segment(word_seg["stem_comp"])
        list_seg_conj = verify_affix(
            word_seg["stem_comp"], list_seg_conj, SNC.NOMINAL_CONJUGATION_AFFIX
        )
        for seg_conj in list_seg_conj:
            stem_conj = word_seg["stem_comp"][: seg_conj[1]]
            suffix = word_seg["stem_comp"][seg_conj[1] :]
            stem_conj = araby.normalize_hamza(stem_conj)
            stem_conj_list = get_stem_variants(stem_conj, suffix)

            for stem in stem_conj_list:
                word_seg_l2 = word_seg.copy()
                # normalize hamza before gessing  differents origines
                word_seg_l2["stem_conj"] = stem
                word_seg_l2["suffix"] = suffix
                # affixes tags contains prefixes and suffixes tags
                word_seg_l2["affix_tags"] = list(
                    set(
                        SNC.COMP_PREFIX_LIST_TAGS[word_seg_l2["pro"]]["tags"]
                        + SNC.COMP_SUFFIX_LIST_TAGS[word_seg_l2["enc"]]["tags"]
                        + SNC.CONJ_SUFFIX_LIST_TAGS[word_seg_l2["suffix"]]["tags"]
                    )
                )
                tmp_list.append(word_seg_l2)

    word_segmented_list = tmp_list
    tmp_list = []
    for word_seg in word_segmented_list:
        inf_noun = word_seg["stem_conj"]
        infnoun_foundlist = lookup_dict(inf_noun)

        for noun_tuple in infnoun_foundlist:
            word_seg_l3 = word_seg.copy()
            word_seg_l3["original"] = noun_tuple["vocalized"]
            word_seg_l3["noun_tuple"] = dict(noun_tuple)
            tmp_list.append(word_seg_l3)

    # test compatiblity noun_tuple with affixes and proaffixes
    # and generate vocalized affixes and suffixes

    word_segmented_list = tmp_list
    tmp_list = []
    for word_seg in word_segmented_list:
        # test if the given word from dictionary accept those
        # tags given by affixes
        if validate_tags(
            word_seg["noun_tuple"],
            word_seg["affix_tags"],
            word_seg["pro"],
            word_seg["enc"],
            word_seg["suffix"],
        ):
            ## get all vocalized form of suffixes
            for pro_voc in SNC.COMP_PREFIX_LIST_TAGS[word_seg["pro"]]["vocalized"]:
                for enc_voc in SNC.COMP_SUFFIX_LIST_TAGS[word_seg["enc"]]["vocalized"]:
                    for suf_voc in SNC.CONJ_SUFFIX_LIST_TAGS[word_seg["suffix"]][
                        "vocalized"
                    ]:
                        ## verify compatibility between proclitics and affix
                        if check_clitic_affix(
                            word_seg["noun_tuple"], pro_voc, enc_voc, suf_voc
                        ):
                            # get affix tags
                            affix_tags_voc = (
                                SNC.COMP_PREFIX_LIST_TAGS[pro_voc]["tags"]
                                + SNC.COMP_SUFFIX_LIST_TAGS[enc_voc]["tags"]
                                + SNC.CONJ_SUFFIX_LIST_TAGS[suf_voc]["tags"]
                            )
                            word_seg_l4 = word_seg.copy()
                            word_seg_l4["suf_voc"] = suf_voc
                            word_seg_l4["enc_voc"] = enc_voc
                            word_seg_l4["affix_tags"] = affix_tags_voc
                            tmp_list.append(word_seg_l4)

    word_segmented_list = tmp_list
    tmp_list = []
    for word_seg in word_segmented_list:
        # get voalized and vocalized without inflection
        # ~ vocalized, semi_vocalized, _ = self.vocalize(
        voca_tuple_list = vocalize(
            word_seg["noun_tuple"]["vocalized"],
            word_seg["pro"],
            word_seg["suf_voc"],
            word_seg["enc_voc"],
        )
        for vocalized, semi_vocalized, _ in voca_tuple_list:
            # add some tags from dictionary entry as
            # mamnou3 min sarf and broken plural
            original_tags = []
            if word_seg["noun_tuple"]["mankous"] == "Tk":
                original_tags.append("منقوص")
            # if there are many cases like feminin plural with mansoub and majrour
            if "cases" in SNC.CONJ_SUFFIX_LIST_TAGS[word_seg["suf_voc"]]:
                list_cases = SNC.CONJ_SUFFIX_LIST_TAGS[word_seg["suf_voc"]]["cases"]
            else:
                list_cases = ("",)
            for case in list_cases:
                voc_affix_case = word_seg["affix_tags"] + (case,)
                # filter empty
                voc_affix_case = [vac for vac in voc_affix_case if vac]
                detailed_result.append(
                    WordCase(
                        {
                            "word": noun,
                            "affix": (
                                word_seg["pro"],
                                "",
                                word_seg["suf_voc"],
                                word_seg["enc_voc"],
                            ),
                            "stem": word_seg["stem_conj"],
                            "root": araby.normalize_hamza(
                                word_seg["noun_tuple"].get("root", "")
                            ),
                            "original": word_seg["noun_tuple"][
                                "vocalized"
                            ],  # original,
                            "vocalized": vocalized,
                            "semivocalized": semi_vocalized,
                            "tags": ":".join(voc_affix_case),
                            "type": ":".join(
                                ["Noun", word_seg["noun_tuple"]["wordtype"]]
                            ),
                            "number": word_seg["noun_tuple"]["number"],
                            "gender": word_seg["noun_tuple"]["gender"],
                            "freq": "freqnoun",  # to note the frequency type
                            "originaltags": ":".join(original_tags),
                            "syntax": "",
                        }
                    )
                )
    return detailed_result


# Fix qalsadi from here
import qalsadi.stem_noun  # noqa

qalsadi.stem_noun.NounStemmer.lookup_dict = lambda _, *args: lookup_dict(*args)
