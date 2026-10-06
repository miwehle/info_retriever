# Marker-Experiment: Sportordnung

`convert.py` verarbeitet `data/sample_pdfs/bds_sportordnung_ipsc_kurzwaffe.pdf` mit Marker 2.0.0 lokal auf der CPU. Wir prüfen insbesondere, ob Kapitel, Unterkapitel und zugehörige Texte korrekt zugeordnet werden. Der Modus `fast` verwendet den PDF-Text und eine Layout-Erkennung. OCR, Formeltranskription und zusätzliche LLM-Verarbeitung sind ausgeschaltet; gescannte Inhalte werden damit nicht zuverlässig erschlossen.

## Starten

In PowerShell aus dem Projektordner, einmalig:

```powershell
python -m venv experiments/marker/.venv
experiments/marker/.venv/Scripts/python.exe -m pip install -r experiments/marker/requirements.txt
```

Experiment ausführen:

```powershell
experiments/marker/.venv/Scripts/python.exe experiments/marker/convert.py
```

Beim ersten Lauf werden Modelle heruntergeladen. Der Modell-Cache liegt unter `.cache/marker` und `.cache/huggingface`. Surya startet für die Layout-Erkennung automatisch einen lokalen Hilfsprozess, der für weitere Aufrufe bestehen bleiben kann; dessen Logs liegen unter `%USERPROFILE%/.cache/datalab/surya`. Die Textextraktion läuft mit einem Worker, um zusätzliche Python-Starts unter Windows zu vermeiden. Die separate virtuelle Umgebung lässt die Docling-Experimente unverändert. Es werden keine kostenpflichtigen Cloud-APIs verwendet.

## Ausgaben und Prüfung

Unter `output/` entstehen Markdown, Bilder, JSON mit Blockpositionen und Abschnittszuordnungen sowie Metadaten. `tree.txt` zeigt die tatsächliche Verschachtelung der JSON-Ausgabe mit Textausschnitten und `section_hierarchy`. `structure.md` listet die Überschriften mit Level, PDF-Seite, ID und Zuordnung. Die JSON-Ausgabe ist Markers Renderer-Ausgabe, kein vollständiger Speicherabzug des internen `Document`. Die Ausgaben bleiben außerhalb von Git und werden beim erneuten Lauf überschrieben.

Prüfkriterien: Liegt „Kapitel 1 – Parcoursgestaltung“ über „1.1 Allgemeine Prinzipien“? Gehören die nachfolgenden Textblöcke zum richtigen Abschnitt, auch über Seitengrenzen hinweg? Werden Anhänge und Divisionsüberschriften richtig zugeordnet? Ein fehlerfrei durchgelaufenes Skript oder gültige Referenzen belegen noch keine fachlich richtige Hierarchie. Das Skript korrigiert keine Erkennungsergebnisse.

## Experiment 2: Überschriftenkorrektur mit OpenAI

`convert2.py` verwendet dieselbe Python-Umgebung und lokale PDF-Verarbeitung. Anschließend ruft es ausschließlich Markers `LLMSectionHeaderProcessor` mit dem OpenAI-Adapter und `gpt-5-mini` auf. Übertragen werden die erkannten, nicht ignorierten Überschriften einschließlich IDs, Reihenfolge, Seiten und Abmessungen. Das PDF und die Seitenbilder werden nicht hochgeladen. Als Überschrift fehlklassifizierter Text kann allerdings ebenfalls im Prompt enthalten sein.

`OPENAI_API_KEY` muss in der Umgebung gesetzt sein oder in `.env` im Projektwurzelordner stehen. Diese Datei ist von Git ausgeschlossen; ein vorhandener Umgebungswert hat Vorrang. Den Schlüssel nicht in die Python-Datei schreiben.

```powershell
experiments/marker/.venv/Scripts/python.exe experiments/marker/convert2.py
```

Die Ergebnisse stehen unter `output/experiment2/`: `before.json` vor der Korrektur, korrigiertes Markdown und JSON, `structure.md`, `tree.txt`, `comparison.md`, `prompt.txt`, `response.json` und getrennte Laufzeiten in `timing.json`. Der Vergleich verwendet denselben lokalen Lauf als Vorher-Zustand. Das erste Experiment wird nicht überschrieben.

Der Marker-Prozessor ändert zunächst das Überschriften-HTML. Das Skript überträgt die korrigierten Level nach `heading_level` und stellt das ursprüngliche HTML wieder her. So erhält auch `section_hierarchy` die Korrektur, während Markers normaler Export die Quellenanker unverändert erzeugt. Es übernimmt ausschließlich die Level bekannter Überschriften. Text und übriges Markup stammen stets aus dem Original; abweichende Modellvorschläge werden im Vergleich vermerkt und verworfen. Unbekannte IDs, doppelte IDs und ungültige Level führen zum Abbruch. Eine fehlgeschlagene API-Anfrage wird nicht als erfolgreiche Korrektur ausgegeben. Fehlende Überschriften und leere, ignorierte Blöcke werden damit nicht repariert.

Der API-Aufruf kostet zusätzlich zum ChatGPT-Abonnement. Für `gpt-5-mini` nennt die [OpenAI-Modellseite](https://developers.openai.com/api/docs/models/gpt-5-mini) am 06.10.2026 0,25 USD je Million Eingabetokens und 2 USD je Million Ausgabetokens; Reasoning zählt zur Ausgabe. Beispielsweise wären 20.000 Eingabe- und 10.000 Ausgabetokens rund 0,025 USD, keine Messung dieses Experiments. Das Modell ist dort inzwischen als deprecated markiert; wir verwenden es hier für den gezielten Versuch mit Markers vorhandenem Adapter. Jeder erneute Skriptlauf führt die Korrektur erneut aus und kann erneut Kosten verursachen.
