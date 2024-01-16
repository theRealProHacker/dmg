# Der erste Anfang

Nun habe ich die nächsten Monate Zeit, um ein Produkt zu schaffen, dass Anderen nutzt und auf das ich stolz sein kann. Gleichzeitig muss ich darauf achten, einen wissenschaftlichen Standard aufrechtzuerhalten und am Ende möchte ich auch eine Bachelorarbeit haben, die einer Publikation wert ist. 

Diese Reihe von "Gedanken" stellt ein Tagebuch für meine Gedanken dar. Dies ist hilfreich, da ich mir oft viele Gedanken mache, diese jedoch nicht aufschreibe, was wodurch es so scheint als hätte ich mir gar keine Gedanken gemacht und meine Entscheidungen arbiträr getroffen. Meine Absicht ist außerdem die Bachelorarbeit am Ende auf Grundlage dieser Notizen zu schreiben. 

## Ein erster Prototyp

Das Ziel ist, so bald wie möglich einen ersten Prototypen zu bauen, der von möglichen Anwendern benutzt werden kann und auf dem dann iteriert werden kann. Dazu müssen wir den Scope zunächst stark verringern.

### Der Scope

Zu Beginn tun wir so, als ob die Transliteration lediglich eine einzige Funktion ist, die einen Text erhält und einen neuen ausspuckt. Diese Funktion sollte zumindest folgende Anforderungen für voll-vokalisierten Text vollständig erfüllen.

- Die korrekte Transliteration von Buchstaben und diakritischen Zeichen
- Die korrekte Anwendung von Pausa

Und folgende Anforderungen teilweise:

- Das korrekte Setzen von Bindestrichen
- Das Großschreiben von Eigennamen
- Assimilationen

Diese Anforderungen habe ich ausgewählt, weil sie die essenziellsten, aber auch einfachsten, Anforderungen darstellen. Dies erlaubt mir, so schnell wie möglich einen nutzbaren Prototypen zu erstellen. Sowohl das vollständig korrekte Setzen von Bindestrichen als auch das Großschreiben von Eigennamen erfordert mehr Daten, die noch gesammelt werden müssen. Die vollständige Anwendung von Assimilationen erfordert mehr Anforderungsermittlung mit erfahrenen Transliterierern. Ich möchte diese Elemente jedoch zumindest im Ansatz schon in die Architektur miteinbeziehen, um später große Codeveränderungen zu vermeiden.

### UI

Die Zielplatform ist Desktop, entweder als lokale App oder als Webapp. Der primäre Use Case schließt ein mobiles Endgerät als Client aus, da er von einem Profi im Büro ausgeht. 

Für den UI-Entwurf würde ich mich an Google Translate orientieren: Eine Eingabetextbox links und eine Ausgabetextbox rechts. Dieser Entwurf scheint simpel und einfach zu benutzen.

Als UI-Framework bietet sich aus meiner Sicht folgendes an:

- Flutter mit Dart
- Electron oder Express mit JS
- Tauri mit Rust
- und Flask mit Python

Warum, lasse ich hier für Kürze aus.

Vorerst habe ich mich für Flask in Python entschieden. Erstens erlaubt es einen lokalen oder globalen Server zu bauen. Außerdem habe ich viel Erfahrung mit sowohl Python als auch Flask. Der größte Vorteil ist jedoch, dass Python viele Bibliotheken bereitstellt, die sehr hilfreich sein werden. Python auch für den Server zu nutzen, erlaubt mir also wahrscheinlich IPC zu vermeiden, falls ich auf Python angewiesen sein sollte. Außerdem scheint mir Python keine großen Nachteile mit sich zu bringen, da kein Wert auf Performance gelegt wird. 

Eine mögliche ALternative wäre Python mit WebAssembly im Browser laufen zu lassen. Das würde den Server unnötig machen und eine statische Webseite produzieren. Dies ist jedoch nur unter Umständen überhaupt möglich.

### Dateisystem

Im ersten Prototypen sollte eine einzige Datei ausreichen. Die genaue Modularisierung möchte ich auf einen späteren Zeitpunkt verschieben, wenn ich mehr Verständnis über die Abhängigkeiten erlangt habe. 

Statische Daten sollten jedoch definitiv in einem eigenen Modul liegen. Dieses bildet dann "a single source of truth". Dynamische Daten können in CSV- und JSON-Dateien gespeichert werden und dann zum Start in den Arbeitsspeicher geladen werden. Falls die Menge an Daten zu groß wird, könnte eine Datenbank in Erwägung gezogen werden.

Der Server- und Testcode sollte auch in eigenen Modulen getrennt sein.

### Architektur

Grundsätzlich programmiere ich intuitiv und ohne mich vorher festzulegen und bisher war ich damit auch bei Abertausenden von Codezeilen sehr erfolgreich. Deswegen werde ich für diesen ersten Prototypen, die Architektur grob und knapp vorstellen, aber nicht mit großen Detail:

- Tokenisierung
- Transliterierung
- Präfixierung
- Eigennamen
- Assimilationen

Zur Tokenisierung reicht vorerst ein einfaches `.split()`, aber natürlich ist das nicht ausreichend für das finale Produkt. Hier geht es aber erst mal vor allem um die anderen Funktionen. 

Für die Transliterierung nutzen wir regex-Ersetzungen mit der `re.sub()`-Methode. Die Reihenfolge der Anwendungen erlaubt große Kontrolle über die genaue Funktionsweise. Hier ist ein früher Entwurf, den ich aber nicht so übernommen habe:

```py
# alif maqsurah
alif_maqsurah -> alif

# hamzah
"^"+hamzah+"$" -> ??? # not sure, but shouldn't be empty string
"^"+hamzah -> ""
hamzah -> "ʾ"

# taa' marbutah
if pausing or not status_constructus:
    ta_marbutah -> "h"
else:
    ta_marbutah -> "t"

# shaddah
for a,l in zip(a_letters, l_letters):
    a+shaddah -> l+l

# yaa' and waw with diacritic sign (except for shaddah)
for a,l in zip(a_diacritics, l_diacritics):
    a_y+a -> "y"+l
    a_w+a -> "w"+l

# vowels with diacritic sign before
fathah+alif -> "ā"
kasrah+a_y -> "ī"
dammah+a_w -> "ū"

# default (half) vowels
alif -> "ā"
a_y -> "y"
a_w -> "w"

# default full consonants
for a,l in zip(a_full_consonants, l_full_consonants):
    a -> l

# diacritics (fatha, kasra, damma, sukun, tanween)
for a,l in zip(a_diacritics, l_diacritics):
    a -> l
```

### Daten

Parallel zur Programmierung werde ich das Arabischinstitut an der FU um Daten zum Trainieren und Testen bitten. Explizit suche ich nach arabischen Texten mit entsprechender Transliteration. Interessant sind auch verschiedene Transliterationspräferenzen.

Weitere Quellen von Transliterationen aus dem Internet sind Transliterationen des Quran (https://www.uni-goettingen.de/de/document/download/43b887124901209d66d40a83d81bc83a.pdf/Koran_transliter.pdf), Transliterationen auf Wikipedia und einzelne Passagen aus wissenschaftlichen Arbeiten, die manuell gesammelt werden müssen. 

### Tests

Ich habe schon ein paar simple Tests in einem seperaten Modul eingeführt. Diese sind hauptsächlich zur Qualitätssicherung, können aber auch für TDD genutzt werden. 

