# Erstes Docling-Experiment

`convert.py` verarbeitet `data/sample_pdfs/Attention Is All You Need.pdf` vollständig mit der Standard-PDF-Pipeline auf der CPU. OCR ist ausgeschaltet, Tabellenanalyse eingeschaltet. Die Konfiguration steht direkt im Skript; zunächst untersuchen wir die Standardausgabe ohne zusätzliche Hierarchieerkennung.

## Starten

In PowerShell aus dem Projektordner, einmalig:

```powershell
python -m venv experiments/docling/.venv
experiments/docling/.venv/Scripts/python.exe -m pip install -r experiments/docling/requirements.txt
```

Konvertieren:

```powershell
$env:HF_HOME = Join-Path (Get-Location) '.cache/huggingface'
experiments/docling/.venv/Scripts/python.exe experiments/docling/convert.py
```

Beim ersten Lauf lädt Docling die benötigten Modelle herunter; dafür ist Internet erforderlich. Die PDF-Verarbeitung erfolgt lokal. Die Laufzeit hängt unter anderem von CPU und Modell-Cache ab.

## Ergebnisse prüfen

Unter `output/` entstehen eine JSON-Datei mit dem vollständigen exportierten `DoclingDocument` und eine Markdown-Datei zum Lesen. Die Konsole zeigt Seitenzahl, Laufzeit und erkannte Überschriften. Die Ausgabe wird bei erneutem Lauf überschrieben und bleibt außerhalb von Git.

Zum Experimentieren einen Breakpoint nach `document = result.document` setzen. Interessant sind `document.body`, `document.texts`, `document.tables` und die Fundstellen in `item.prov` mit Seite und Begrenzungsrechteck. JSON lässt sich später mit `DoclingDocument.load_from_json(path)` aus `docling_core.types.doc` wieder laden, ohne erneut zu konvertieren.

Zunächst vergleichen wir Textreihenfolge, Überschriften, Tabellen und Fundstellen mit dem Original. Erkannte Überschriften allein belegen noch keine korrekt rekonstruierte Kapitelhierarchie.

## Zweites Experiment: Bilder und Formeln

`convert2.py` ergänzt Bildausschnitte mit doppelter Auflösung und Formelerkennung als LaTeX. Das erste Skript und seine Ergebnisse bleiben unverändert. Die zusätzliche Formelerkennung lädt beim ersten Lauf ein weiteres Modell und benötigt auf der CPU mehr Zeit.

```powershell
$env:HF_HOME = Join-Path (Get-Location) '.cache/huggingface'
experiments/docling/.venv/Scripts/python.exe experiments/docling/convert2.py
```

Die Ergebnisse stehen unter `output/experiment2/`: JSON, Markdown und ein Ordner mit verlinkten PNG-Bildern. Die Markdown-Vorschau muss LaTeX-Mathematik unterstützen (beispielsweise die Vorschau in VS Code). Beim Weitergeben der Markdown-Datei den Bilderordner mitnehmen. Die erkannten Formeln müssen mit dem Original verglichen werden; nichtleerer Formeltext allein belegt keine korrekte Erkennung.

Der Markdown-Export setzt die Formeltexte in eine LaTeX-`aligned`-Umgebung, damit enthaltene Ausrichtungszeichen und Zeilenumbrüche dargestellt werden können. Der JSON-Export behält die unveränderten Erkennungsergebnisse. Im ersten CPU-Lauf wurden 15 Seiten mit 7 Bildern und 6 Formeltexten in rund 536 Sekunden verarbeitet, einschließlich des erstmaligen Modelldownloads. Die Transformer-Abbildung ist vorhanden; die Lernratenformel enthält erkennbare Transkriptionsfehler.

## Drittes Experiment: Formeln als Originalausschnitte

`convert3.py` verarbeitet ebenfalls das Attention-Paper. Die Formeltranskription ist ausgeschaltet. Stattdessen werden erkannte Formel- und Bildbereiche aus gerenderten PDF-Seiten ausgeschnitten und als PNG ins Markdown eingebunden, jeweils mit einem Link auf die PDF-Seite im Original. Die Bereichserkennung kann weiterhin Fehler machen; die Formelinhalte werden jedoch nicht von einem Modell neu geschrieben. Inline-Formeln innerhalb von Fließtext werden damit nicht automatisch zu separaten Bildern.

```powershell
$env:HF_HOME = Join-Path (Get-Location) '.cache/huggingface'
experiments/docling/.venv/Scripts/python.exe experiments/docling/convert3.py
```

Die Ergebnisse stehen unter `output/experiment3/`. Die relativen Bildlinks benötigen den Unterordner `images/`; die Quellenlinks setzen die bestehende Projektstruktur voraus. Ob ein PDF-Link direkt zur angegebenen Seite springt, hängt vom verwendeten Viewer ab. JSON enthält die Dokumentstruktur und Fundstellen, aber keine gerenderten Seitenbilder. Die vorherigen Experimente bleiben unverändert.

Der geprüfte CPU-Lauf benötigte rund 50 Sekunden bei bereits vorhandenen Modellen und erzeugte 7 Abbildungs- und 6 Formelbilder. Die Links wurden geprüft und die Attention- sowie Lernratenformel visuell kontrolliert. Experiment 2 benötigte rund 536 Sekunden einschließlich erstmaligem Modelldownload; allein seine Formeltranskription dauerte rund 395 Sekunden. Die Zeiten sind daher kein kontrollierter Benchmark, zeigen aber den eingesparten Rechenschritt.

## Viertes Experiment: IPSC-Sportordnung

`convert4.py` verarbeitet `data/sample_pdfs/bds_sportordnung_ipsc_kurzwaffe.pdf` vollständig auf der CPU mit denselben Einstellungen wie Experiment 3. Es verwendet dessen Exportklassen wieder: erkannte Bilder und mögliche Formelbereiche werden als Originalausschnitte mit PDF-Seitenverweis ausgegeben. Formeltranskription und OCR bleiben ausgeschaltet; Tabellenanalyse ist aktiviert.

```powershell
$env:HF_HOME = Join-Path (Get-Location) '.cache/huggingface'
experiments/docling/.venv/Scripts/python.exe experiments/docling/convert4.py
```

Markdown, JSON und der Unterordner `images/` entstehen unter `output/experiment4/`. Die Einschränkungen zu Bereichserkennung, Inline-Formeln und relativen Quellenlinks aus Experiment 3 gelten weiterhin. Die Anzahl erkannter Formelbereiche ist keine Aussage darüber, ob das Original tatsächlich keine weiteren Formeln enthält.

## Fünftes Experiment: Kapitelhierarchie der Sportordnung

`convert5.py` aktiviert zusätzlich `HeadingHierarchyOptions(enabled=True)` und erhält mit `generate_parsed_pages=True` die für Schriftmerkmale benötigten Daten. Docling kann so Lesezeichen, Nummerierung und Schriftmerkmale für Überschriftenebenen auswerten. Die übrige Verarbeitung entspricht Experiment 4, ohne Formeltranskription.

```powershell
$env:HF_HOME = Join-Path (Get-Location) '.cache/huggingface'
experiments/docling/.venv/Scripts/python.exe experiments/docling/convert5.py
```

Unter `output/experiment5/` stehen neben Markdown, JSON und Bildausschnitten zwei Prüfdateien: `tree.txt` zeigt die tatsächlichen Eltern-Kind-Beziehungen mit Einrückung (Text pro Knoten auf 120 Zeichen gekürzt); `structure.md` enthält Kennzahlen und alle Überschriften mit Ebene, PDF-Seite und Elternreferenz. Es wird kein eigener Kapitelbaum konstruiert. Die installierte Hierarchie-Funktion weist vor allem `level`-Werte zu; deren Veränderung allein erfüllt unser Erfolgskriterium einer korrekten Verschachtelung nicht.
