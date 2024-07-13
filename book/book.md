# Dieses Tool

Dies ist ein Tool, dass Ihnen bei der Transliteration des Arabischen nach dem Standard der Deutschen Morgenländischen Gesellschaft (DMG) hilft. Im Großen und Ganzen transliteriert das Tool vollautomatisch. Auf die Richtigkeit der Ausgabe gibt es jedoch keine Garantie. Deswegen ist es sehr wichtig, dass Sie immer eine rigorose Überprüfung anwenden. 

# Das UI

Das UI ist einfach gehalten, um den Fokus auf die Transliteration zu legen. Hier eine Übersicht

<div class="col-11 p-1 bg-white">
    <div class="ratio ratio-16x9">
        <img src="/static/ui.png" alt="UI Übersicht">
    </div>
</div>
<br>

Die **Aktionsleiste**/das **Aktionsmenü** stellt einige wichtige Funktionen bereit

- Das **Handbuch** ist das Dokument, das Sie gerade lesen. Hier können Sie immer wieder zurückkommen
- Außerdem können Sie **Feedback** zum Tool geben. Jedes Feedback ist willkommen und wird zur Verbesserung des Tools verwendet. Beachten Sie jedoch [die bekannten Fehler](#bekannte-fehler)
- Es gibt auch eine digitale arabische **Tastatur** zur [Eingabe](#eingabe)
- Natürlich darf auch ein **Dark-Mode** nicht fehlen
- Um die Transliteration flexibel zu gestalten und die vielen verschiedenen Standards zu berücksichtigen, gibt es einige **[Einstellungen]**(#einstellungen), die in einer Side Bar angezeigt werden

Im **Eingabefeld** kann ein arabischer Text eingegeben werden. Dieser wird dann automatisch transliteriert und die Transliteration wird im **Ausgabefeld** angezeigt. Durch Klicken kann das Ergebnis in die Zwischenablage kopiert werden. Unterhalb des Ausgabefeldes können Sie angeben, ob Sie mit dem Ergebnis zufrieden sind. Diese Angaben werden verwendet, um das Tool zu verbessern. 

Beachten Sie bitte, dass der arabische Text nicht vokalisiert wird. Das müssen Sie entweder manuell tun, oder Sie lassen den Text durch eine KI automatisch vokalisieren, indem sie auf den "magischen" **Vokalisation**sknopf drücken. Das braucht zwar oft ziemlich lange, also so um die 10 Sekunden, aber die KI wird zu 90 % korrekte Ergebnisse liefern. 

Falls Sie im Aktionsmenü die virtuelle arabische **Tastatur** ausgeklappt haben, dann wird diese unterhalb der beiden Textfelder angezeigt und kann sehr intuitiv benutzt werden. Die Tastatur enthält alle gängigen Zeichen. 

## Eingabe

Einer der großen Schwierigkeiten bei der Transliteration nach dem Standard der DMG ist die digitale Eingabe. Eigentlich muss man mit drei verschiedenen Tastaturen hantieren: einer arabischen, einer normalen deutschen und einer für die Zeichen der Transliteration. 

> Übrigens gibt es [hier](https://github.com/sixtyfive/de_dmg) "Windows- und Linux-Tastatur-Layouts zum Setzen von Texten mit Persischen/Arabischen Phonemen nach dem Transliterationssystem der Deutschen Morgenländischen Gesellschaft"

Dieses Tool stellt zwei alternative Eingabemöglichkeiten für Arabisch bereit, um das ständige Wechseln zwischen Tastaturen zu vermindern. Zunächst gibt es eine ausklappbare digitale arabische Tastatur, auf die man mit dem Tastatursymbol oben in dem Aktionsmenü rechts auf der Navigationsleiste zugreifen kann. Es ist jedoch auch möglich, mit einer deutschen Tastatur die allermeisten arabischen Buchstaben und Zeichen zu schreiben. Dabei gilt generell, dass die meisten Buchstaben ihrem deutschen oder (hauptsächlich) englischen Lautwert entsprechen, emphatische Buchstaben aber großgeschrieben werden. Andere Buchstaben sind ihrem Aussehen entsprechend repräsentiert (e → ع, ö → ة), ihrer IPA-Umschrift nach (x → خ) oder nahezu zufällig. Zu Beginn muss man vielleicht noch ab und zu hier reinschauen, doch relativ schnell hat man das nötige Muskelgedächtnis entwickelt, um sehr schnell mit einer deutschen Tastatur zu tippen. 

<details>

<summary>Zuordnung der Zeichen von Deutsch zu Arabisch</summary>
input_map

</details>

<br>

# Bekannte Fehler

> Es gilt im Allgemeinen: Je genauer Sie die Eingabe vokalisieren, desto besser wird die Ausgabe Ihren Vorstellungen entsprechen. 

1. Die KI zur **Vokalisation** gleicht architektonisch LLMs wie ChatGPT und ist daher immer anfällig für sogenannte Halluzinationen, also völlig schwachsinnige, nicht-nachvollziehbare Ausgaben
2. Die Erkennung der Präfixe und Genetivkonstruktionen scheitert teilweise. Dann ist es meist das Beste die fehlenden Zeichen (t bzw. -) einfach später selbst nachzutragen. Oft ist es aber auch hilfreich, noch spezifischer zu werden und zum Beispiel eine weitere *ḥaraka* einzufügen:
    - الكِتاب → alkitāb, aber الكِتَاب → al-kitāb
    - هَمزَة الوَصل → hamza al-waṣl, aber هَمزَة الوَصلِ → hamzat al-waṣl. Die *kasra* macht dem Programm klar, dass "al-waṣl" im Genetiv steht
3. Wenn ein Imperativ mit *hamzat al-waṣl* beginnt, auf das ein *lām* folgt, auf das ein Konsonant folgt, welcher keine *ḍamma* trägt, wird das *hamzat al-waṣl* als "a" nicht als "i" wiedergegeben. In solchen Fällen, kann der Kurzvokal auf dem *hamzat al-waṣl* explizit gesetzt werden: العَب (Spiel!) → alʿab, aber اِلعَب → ilʿab
4. Außer einige wenige Ausahmen, wie Allāh, werden Namen nicht großgeschrieben. Für Namen gibt es stattdessen ein [dediziertes Tool](/names), welches über die Navigationsleiste erreicht werden kann. 

# Einstellungen

Die Einstellungen sind einfache boolesche Switches, können also entweder an oder aus sein. Durch Klicken kann man zwischen den beiden Zuständen hin- und herwechseln. Durch Hovern kann man für jede Einstellung eine kurze Beschreibung und jeweils ein Beispiel für den An- und Aus-Zustand sehen. 

## Allgemeine Einstellungen
- **Pausa** (aus)  
    Bei der Transliteration gibt es zwei grundlegend verschiedene Arten zu transliterieren: die Pausal- und die voll vokalisierte Form. Bei der gebräuchlicheren Pausalform werden die Flexionsendungen weggelassen, außer bei: 
    - Verben
    - Präpositionen
    - Pronomen, auch suffigiert
    - Konjunktionen
    - Akkusativendungen
- **Tāʾ marbutah** (aus)  
    Das *tāʾ marbutah* kann, falls keine Flexionsendungen folgen, kein langer Vokal davorsteht und keine Genetivverbindung besteht, entweder als h oder gar nicht wiedergegeben werden. Die Einstellung gibt an, ob das *tāʾ marbutah* wiedergegeben wird.
- **Diphthonge** (aus)  
    Diese Einstellung bestimmt, ob Diphthonge vokalisch wiedergegeben werden. Also ai/au statt ay/aw. 
- **Geminierte Halbvokale** (an)  
    Diese Einstellung bestimmt, ob Halbvokale mit Shaddah als doppelte Konsonanten wiedergegeben werden. Also iyy/uww statt īy/īw
- **-ī und -ū** (an)  
    Diese Einstellung bestimmt, ob die gerade in **Geminierte Halbvokale** erwähnten Halbvokale am Ende von Wörtern unabhängig von der oben gesetzten Einstellung immer als -ī/-ū wiedergegeben werden. Beachten Sie, dass die männliche Nisbaendung immer so wiedergegeben wird. 
- **Anlautendes Hamza** (aus)  
    Diese Einstellung bestimmt, ob ein anlautendes *hamzat al-qaṭ* wiedergegeben wird. Ein *hamzat al-waṣl* wird nie wiedergegeben
- **-hu und -hi** (an)  
    Diese Einstellung bestimmt, ob das suffigierte Personalpronomen der 3. Pers. Sing. Masc. nach einer kurzen Silbe verlängert wird. 

## Einstellungen für Namen

Namen werden grundsätzlich in Pausa wiedergegeben

- **Buchtitel**  
    Bei Namen kann man zwischen Personen- und Ortsnamen sowie Buchtiteln unterscheiden. Bei Buchtiteln wird nur das erste Wort großgeschrieben, außer das erste Wort ist *Kitāb*, dann wird auch das nächste großgeschrieben. Personen und Ortsnamen werden bis auf die Abstammungspartikel *ibn*, *bin* und *bint* grundsätzlich vollständig großgeschrieben. 
- **b. und bt.**  
    Bei Personennamen können die gerade erwähnten Abstammungspartikel *ibn*, *bin* und *bint* mit b. und bt. abgekürzt werden. 
