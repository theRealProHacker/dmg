# Specification

This is a live documentation that details how the current code works and explains design decisions

## Open Questions

- When exactly will a ta marbutah be transliterated as a "t", as an "h" or
not at all?
- Follow-up: When exactly is a genitive construction (idafah) in place?
- What kind of settings should be available? What kind of texts will be
transliterated most of the time?
- How should single letters be transliterated?
- What punctuation should be transliterated how?
    - Currently: ".!?,"

## UI

A sleek and modern UI

- Dark/light mode switch
- Color contrast: white, black, gold and purple
- Responsive
- Useful navbar
- Beautifully extendable sidebar

## Tokenization

...

## Ta marbutah

Option: "Ta marbutah"

The ta marbutah is a special Arabic character that only appears in nouns and adjectives (but not in verbs or stopwords). The character can be romanized as either "t", "h" or not at all. This depends on the grammatical context and the user preference. 

If the noun is the first word (nomens regens) of an idafah (see below) then the ta marbutah is romanized as "t". In every other case it is romanized as "h" or not. If the ta marbutah is not the last letter or a long vowel is before it, then it must be romanized as "h". Else, the romanizer can choose whether he wants to keep the ta marbutah or not. This is represented in the "Ta marbutah" flag. 

> Bei einer Idafah / Genitivverbindung stehen zwei Nomen in einer Verbindung, die eine Zugehörigkeit oder einen Besitz ausdrücken. Das erste Nomen (nomen regens) steht immer ohne Artikel, aber mit bestimmter Nunation. Das zweite Nomen (nomen rectum) steht im Genitiv. Wenn er mit Artikel steht, handelt es sich um eine bestimmte Genitivverbindung. 

> (translated) In an idafah (genetive construction) two nouns are connected to indicate a link or ownership. The first noun (Latin: nomens regens) is definite but without article; the case doesn't matter. The second noun must be in the genitive case (which gives the genetive construction it's name). 

## Assimilation

...

## NER

...

## Full vocalisation

...


## Hamzatul wasl

The hamzatul wasl is skipped if one reads "through" it. It can only appear in front of a word and these are the general cases where it can appear:

- article
    - and variations as in `الَّذينَ` (alladheena)
- certain nouns
    - (iṯnāni / iṯnayni / iṯnatāni / iṯnatayni) اثنان / اثنين / اثنتان / اثنتين - two in different forms
    - (ibn - son) ابن
    - (ism - name) اسم
    - (imraʾa - women) امرأة
- Verb stems VII-X
    - verbs and nouns
    - Without the defected forms
    [![Verbstems image](verb-stems-7-to-10.png)](https://en.wikipedia.org/wiki/Arabic_verbs)

There are two characters that can be used to indicate a hamzatul wasl. The first is the normal alif. The other is a special hamzatul wasl glyph. An initial alif is however no guarantee that there is a hamzatul wasl. 

The hamzatul wasl has an implicit short vowel that is pronounced when one doesn't read "through" it. This vowel is almost always "i" as you can observe above. When it represents an article, it's an "a". Very rarely it could also be a "u", but we will ignore this possibility.

Whether one reads "through" the hamzatul wasl depends on the ending of the previous word. Specifically, if it ends an a vowel sound, then you read on. The first word of a sentence is always attacked and cannot be read through.

So let's start first with the article: It is determined with the rest of the prefixes and is transliterated as "(a)l". The rest needs to be a noun. The word "alladheena" and similar words like "alladhee" can be transliterated completely seperately. 

If a word start with a hamzatul wasl it is transliterated as "(i)" except if it already has a short vowel, then that replaces the i. 

For a starting alif, we need to check whether the word fits into one of the words that have a hamzatul wasl. If that is the case, the alif is transliterated as "(i)" else as "ā". 

## Special words

- alladhee, alladheena
- ism, ibn, imra'a, ithnan, etc.
- Pronouns: ana, huwa, hiya, hadha
- Prepositions: fi, ila, lahu, laka, etc.
- special clearly foreign words (like beige)

## An overview of what a character can turn into

Assuming that a shaddah doubles a character each character can be transformed into some exactly predetermined set of characters without exceptions.

- ء: "", ʾ
- ب: b
- ت: t
- ة: "", h, t
- ث: ṯ
- ج: ǧ
- ح: ḥ
- خ: ḫ
- د: d
- ذ: ḏ
- ر: r
- ز: z
- س: s
- ش: š
- ص: ṣ
- ض: ḍ
- ط: ṭ
- ظ: ẓ
- ع: ʿ
- غ: ġ
- ف: f
- ق: q
- ك: k
- ل: l
- م: m
- ن: n
- ه: h

- و: u, ū, w
- ي: i, ī, y
- ا: "", a, ā 
- ٱ: ""
- ى and آ: ā
- ِ: "", a
- ُ: "", u
- ِ: "", i

> An exception is when the double vowel setting is used. However, that can be done in post processing: uww -> ūw, iyy -> īy


## Unicode cleanup

Unicode has a lot of Arabic characters that only distinguish the representation of letters. For example, letters can take different forms depending on their position in a word. 

However, we don't care about any representational forms and therefore it is necessary to replace them with their semantic equivalents. More information can be found [on Wikipedia](https://en.wikipedia.org/wiki/Arabic_script_in_Unicode#Compact_table)

<details>
<summary>Full table</summary>

```py
"ﭐ": alif_wasl,
"ﭑ": alif_wasl,
"ﮪ": "ه",
"ﮫ": "ه",
"ﮬ": "ه",
"ﮭ": "ه",
"ﺀ": "ء",
"ﺃ": hamza,
"ﺄ": hamza,
"ﺅ": hamza,
"ﺆ": hamza,
"ﺇ": hamza,
"ﺈ": hamza,
"ﺉ": hamza,
"ﺊ": hamza,
"ﺋ": hamza,
"ﺌ": hamza,
"ﺍ": alif,
"ﺎ": alif,
"ﺏ": "ب",
"ﺐ": "ب",
"ﺑ": "ب",
"ﺒ": "ب",
"ﺓ": "ة",
"ﺔ": "ة",
"ﺕ": "ت",
"ﺖ": "ت",
"ﺗ": "ت",
"ﺘ": "ت",
"ﺙ": "ث",
"ﺚ": "ث",
"ﺛ": "ث",
"ﺜ": "ث",
"ﺝ": "ج",
"ﺞ": "ج",
"ﺟ": "ج",
"ﺠ": "ج",
"ﺡ": "ح",
"ﺢ": "ح",
"ﺣ": "ح",
"ﺤ": "ح",
"ﺥ": "خ",
"ﺦ": "خ",
"ﺧ": "خ",
"ﺨ": "خ",
"ﺩ": "د",
"ﺪ": "د",
"ﺫ": "ذ",
"ﺬ": "ذ",
"ﺭ": "ر",
"ﺮ": "ر",
"ﺯ": "ز",
"ﺰ": "ز",
"ﺱ": "س",
"ﺲ": "س",
"ﺳ": "س",
"ﺴ": "س",
"ﺵ": "ش",
"ﺶ": "ش",
"ﺷ": "ش",
"ﺸ": "ش",
"ﺹ": "ص",
"ﺺ": "ص",
"ﺻ": "ص",
"ﺼ": "ص",
"ﺽ": "ض",
"ﺾ": "ض",
"ﺿ": "ض",
"ﻀ": "ض",
"ﻁ": "ط",
"ﻂ": "ط",
"ﻃ": "ط",
"ﻄ": "ط",
"ﻅ": "ظ",
"ﻆ": "ظ",
"ﻇ": "ظ",
"ﻈ": "ظ",
"ﻉ": "ع",
"ﻊ": "ع",
"ﻋ": "ع",
"ﻌ": "ع",
"ﻍ": "غ",
"ﻎ": "غ",
"ﻏ": "غ",
"ﻐ": "غ",
"ﻑ": "ف",
"ﻒ": "ف",
"ﻓ": "ف",
"ﻔ": "ف",
"ﻕ": "ق",
"ﻖ": "ق",
"ﻗ": "ق",
"ﻘ": "ق",
"ﻙ": "ك",
"ﻚ": "ك",
"ﻛ": "ك",
"ﻜ": "ك",
"ﻝ": "ل",
"ﻞ": "ل",
"ﻟ": "ل",
"ﻠ": "ل",
"ﻡ": "م",
"ﻢ": "م",
"ﻣ": "م",
"ﻤ": "م",
"ﻥ": "ن",
"ﻦ": "ن",
"ﻧ": "ن",
"ﻨ": "ن",
"ﻩ": "ه",
"ﻪ": "ه",
"ﻫ": "ه",
"ﻬ": "ه",
"ﻭ": "و",
"ﻮ": "و",
"ﻯ": "ى",
"ﻰ": "ى",
"ﻱ": "ي",
"ﻲ": "ي",
"ﻳ": "ي",
"ﻴ": "ي",
"ﻵ": "ل" + alif_maddah,
"ﻶ": "ل" + alif_maddah,
"ﻷ": "ل" + hamza,
"ﻸ": "ل" + hamza,
"ﻹ": "ل" + hamza,
"ﻺ": "ل" + hamza,
"ﻻ": "لا",
"ﻼ": "لا",
```

</details>

Another problem is that in the Unicode specification the shaddah is supposed to come after any other short vowel. However, it makes much more sense to swap their position instead. 