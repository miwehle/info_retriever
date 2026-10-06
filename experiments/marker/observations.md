# Beobachtungen: Marker und die Sportordnung

Geprüfter Lauf am 06.10.2026 mit Marker 2.0.0 und Surya 0.22.1: alle 104 PDF-Seiten verarbeitet, CPU, `fast`, OCR und zusätzliche LLM-Verarbeitung ausgeschaltet, ein Worker für PDF-Textextraktion. Rund 87 Sekunden ab Modellinitialisierung bis einschließlich Export; Python-Imports und vorherige Einrichtungsversuche sind darin nicht enthalten. Kein kontrollierter Laufzeitvergleich mit Docling.

- Die Ausgabe enthält 157 Überschriften und 73 Markdown-Bildlinks. Die JSON-Seitenzahl, alle Bildlinks und die Auflösbarkeit der `section_hierarchy`-Referenzen wurden geprüft.
- Alle zwölf Überschriften „Kapitel n …“ sind Level 1. Das ist besser als die falschen Kapitel-Level im bisherigen Docling-Experiment.
- Die native Ausgabe ist nach Seiten und Blöcken organisiert. `section_hierarchy` ergänzt logische Abschnittszuordnungen: Der Textblock `/page/8/Text/212` mit Regeln ab 1.1.1 verweist beispielsweise auf Kapitel 1 und Abschnitt 1.1.
- Die Unterkapitel-Level sind jedoch inkonsistent: 1.1 hat Level 4, 1.2 Level 3 und 1.3 Level 1. Bei 1.3 ersetzt die Abschnittszuordnung deshalb Kapitel 1. Auch 3.1 und 3.2 stehen auf demselben Level wie Kapitel 3 und verdrängen dessen Zuordnung.
- 1.2.1 und die folgenden Regeln 1.2.1.1 bis 1.2.1.3 sind sämtlich Level 4. Die Regeln verdrängen damit den Abschnitt 1.2.1 in der Hierarchie, statt darunter zu liegen.
- Die Divisionsüberschriften „Appendix D2: Standard Division“ und „Appendix D3: Classic Division“ sind als Level 1 erkannt. Die korrekte Zuordnung sämtlicher Inhalte und Folgeseiten ist damit noch nicht nachgewiesen.
- Einige gerenderte Überschriftsblöcke haben leeres HTML, beispielsweise `/page/14/SectionHeader/5`, und erscheinen trotzdem in Abschnittszuordnungen. Die Berichte zeigen diese Ergebnisse unverändert.

Fazit: Marker bietet eine direkt auswertbare logische Abschnittszuordnung und erkennt die Kapitelüberschriften in diesem Versuch besser. Eine verlässlich richtige Kapitel- und Unterkapitelhierarchie liefert aber auch diese Konfiguration nicht. Eine allgemeine Qualitätsaussage über andere Marker-Konfigurationen folgt daraus nicht.

Prüfdateien: [structure.md](output/structure.md), [tree.txt](output/tree.txt) und [vollständiges JSON](output/bds_sportordnung_ipsc_kurzwaffe.json).

## Experiment 2: OpenAI korrigiert Überschriften-Level

Am 07.10.2026 wurden 137 nicht ignorierte Überschriften mit Markers eingebautem Überschriften-Prompt an `gpt-5-mini` übergeben. Ein echter API-Aufruf lieferte 78 Levelkorrekturen. Für die anschließenden technischen Reparaturen und Exportprüfungen wurde dieselbe gespeicherte Antwort erneut angewendet; es gab dafür keine weiteren Modellaufrufe. Die Korrekturzeit in der vorliegenden `timing.json` misst deshalb nur die lokale Wiederanwendung, nicht die OpenAI-Latenz.

- Kapitel 1 bleibt Level 1; 1.1, 1.2 und 1.3 erhalten Level 2. 1.2.1 erhält Level 3, seine nummerierten Regeln bleiben Level 4. Auch 3.1 und 3.2 werden von Level 1 auf Level 2 korrigiert.
- Bei 23 Vorschlägen änderte das Modell zusätzlich Text oder Markup, unter anderem beschädigte Umlaute. Diese Änderungen werden verworfen: Nur die Level-Zahl wird übernommen, der Originalinhalt bleibt erhalten.
- Markers Prozessor ändert HTML, synchronisiert aber nicht automatisch `heading_level`. Außerdem kann der Export beim Übernehmen gerenderten HTMLs Quellenanker verdoppeln. Das Experiment übernimmt deshalb nur die korrigierten Level in das native Modell und stellt dessen ursprüngliches HTML wieder her.
- Die Verbesserung betrifft erkannte Überschriften. Fehlende Überschriften und leere, ignorierte Blöcke bleiben bestehen; eine vollständig richtige Dokumenthierarchie ist damit noch nicht nachgewiesen.

Prüfdateien: [Vorher-Nachher-Vergleich](output/experiment2/comparison.md), [Struktur](output/experiment2/structure.md), [gesendeter Prompt](output/experiment2/prompt.txt) und [unveränderte Modellantwort](output/experiment2/response.json).
