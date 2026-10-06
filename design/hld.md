# Info Retriever – High-Level Design

**Status: Konsolidierter Entwurf.** Technische Umsetzung und Freigaben stehen im [LLD](lld.md).

## Ziel und Prinzipien

Info Retriever hilft, Informationen zu finden und direkt an Originalfundstellen zu prüfen. Der MVP ist ein Experiment mit einem textbasierten PDF: Finden wir passende Stellen auch bei anders formulierten Fragen, entdecken wir zusätzliche relevante Informationen und können wir Treffer schnell im Kontext beurteilen? Deutsch und Englisch stehen im Mittelpunkt, einschließlich deutscher Fragen zu englischen Texten. Ein erstes Beispieldokument ist die 104-seitige BDS-IPSC-Sportordnung. KI-Entwicklung zu lernen ist ein wesentliches Projektziel; Vermarktung ist optional.

**Anfrage → sortierte Fundstellen → Auswahl → Original prüfen.** Die Quelle bleibt das maßgebliche Arbeitsobjekt (Original first, Retrieval first). Der Mensch vergleicht und bewertet die Treffer. Ein Ähnlichkeitswert bestätigt nicht den Geltungsbereich einer Aussage. Gerade bei ähnlich aufgebauten Regelabschnitten muss der Kontext erkennbar bleiben; eine echte Passage mit falscher Zuordnung wäre irreführend.

KI ist bereits im MVP durch das Embedding-Modell zentral. Später kann sie die Auswahl und Aufbereitung von Informationen weiter unterstützen. Generierte Texte bleiben an den Originalquellen überprüfbar; die Entscheidung über ihre Verwendung bleibt beim Menschen.

## Mentales Modell des Frontends

Die folgende ASCII-Skizze bewahrt das ursprüngliche Zielbild. Die vier Relevanzbalken je Treffer sind eine spätere Erweiterung; im MVP genügen Originaltext, Fundstellenangabe und ein Suchscore. „KI-Seitenleiste“ bezeichnet den Suchbereich und setzt kein Chat-Modell voraus.

```text
Browser-Tab
┌─────────────────────────────────────────────────────────────────┐
│ Info Retriever                                                  │
├──────────────────────────────────┬──────────────────────────────┤
│ PDF-Viewer                       │ KI-Seitenleiste              │
│                                  │                              │
│ Seite 37                         │ Suchfeld                     │
│ ┌──────────────────────────────┐ │ ┌──────────────────────────┐ │
│ │                              │ │ │ Wie funktioniert ... ?   │ │
│ │ Text ...                     │ │ └──────────────────────────┘ │
│ │                              │ │                              │
│ │ █ relevante Passage █       │ │ Ergebnisliste / RRL         │
│ │                              │ │                              │
│ │ weiterer Text ...            │ │ 1. Treffer                  │
│ │                              │ │    Kapitel      ████████    │
│ └──────────────────────────────┘ │    Unterkapitel ███████     │
│                                  │    Absatz       █████████   │
│ Seite 36  ←  37  →  Seite 38    │    Satz         ██████████  │
│                                  │                              │
│                                  │ 2. Treffer                  │
│                                  │    ...                       │
└──────────────────────────────────┴──────────────────────────────┘

Auswahl eines Treffers
        ↓
PDF-Viewer springt zur Fundstelle
        ↓
relevante Passage wird hervorgehoben
```

Die Seitenleiste enthält Anfrage und nach Relevanz sortierte Ergebnisliste (Ranked Result List, RRL). Im Viewer bleibt normales Lesen, Blättern, Textauswählen und Kopieren möglich. Die Auswahl führt zur Passage, ohne den umgebenden Kontext zu verlieren.

## MVP-Use-Cases aus Benutzersicht

### UC 1 – PDF zum Durchsuchen öffnen

Der Benutzer wählt ein textbasiertes PDF. Die Anwendung bereitet es auf; anschließend ist es angezeigt und durchsuchbar. Nicht lesbare oder nicht unterstützte Dateien werden verständlich gemeldet. Die internen Schritte muss der Benutzer nicht einzeln auslösen.

Dokumentgliederung und Zuordnung der Fundstellen sollen am Original nachvollziehbar sein. Automatisch erkannte Strukturen können Fehler enthalten; unsichere Kapitelzuordnungen dürfen nicht als gesichert dargestellt werden.

### UC 2 – Informationen im PDF suchen

Bei vorbereitetem Dokument gibt der Benutzer eine natürlichsprachliche Anfrage ein, typischerweise eine Frage. Er erhält eine nach Relevanz sortierte Liste mit Originaltext, Fundstellenangaben und Suchscore. Gesucht wird in Dokumentelementen auf mehreren Hierarchieebenen; wie Treffer verschiedener Ebenen zusammengeführt werden, ist im LLD noch zu klären.

### UC 3 – Fundstelle im Original prüfen

Der Benutzer wählt einen Treffer. Der PDF-Viewer springt zur zugehörigen Stelle und hebt die Passage hervor. Der Benutzer kann ihren Geltungsbereich und Kontext prüfen, weiterblättern oder einen anderen Treffer auswählen.

Im MVP entspricht die Markierung dem gefundenen Dokumentelement, etwa einem Absatz oder Satz. Die exakte Anzeige dieses Elements ist von einer späteren anfragebezogenen Auswahl nur seiner relevanten Teile zu unterscheiden.

## MVP-Abgrenzung und Erfolg

Der MVP ist eine lokale Web-Anwendung mit einem aktiven textbasierten PDF. Er verbindet semantische Suche und präzise Originalanzeige. Kein Chat-Modell, keine Agentensteuerung, keine generierten Zusammenfassungen oder Synthese, keine intelligenten Rückfragen, keine einstellbare mehrdimensionale Gewichtung, keine OCR, Browser-Extension oder weiteren Ressourcentypen.

Automatisierte Tests prüfen technische Korrektheit. Den praktischen Nutzen beurteilen wir zusätzlich anhand echter Fragen und erwarteter Fundstellen. Erfolgreiche Suche und korrekte Quellenzuordnung werden getrennt betrachtet. Technische Details stehen im [LLD](lld.md).

## Spätere Ideen – nicht Teil des MVP

- **Präzisere Passagenauswahl:** Innerhalb eines Treffers nur die zur Anfrage passenden Sätze oder Textspannen auswählen. Ein erster Ansatz vergleicht die Satz-Embeddings mit der Anfrage; alternativ könnte ein Chat-Modell unterstützen. Wichtiger Kontext wie Einschränkungen oder Überschriften darf dabei nicht verloren gehen. Das Backend wählt Originaltextspannen aus und ordnet sie ihren PDF-Positionen zu; der Viewer markiert sie. Die Qualität der Auswahl wird gesondert geprüft.
- **Mehrdimensionale Relevanz:** Kapitel, Unterkapitel, Absatz und Satz erhalten eigene Werte; Benutzergewichte bestimmen einen Gesamtscore, beispielsweise `wK·Kapitel + wU·Unterkapitel + wA·Absatz + wS·Satz`. Eine „Warum?“-Ansicht verbindet Score mit Evidenz und optional einer Erklärung.
- **Intelligente Rückfragen:** Top-K-Treffer betrachten, nur offene Präferenzdimensionen berücksichtigen, deren vergleichbar skalierte Streuung untersuchen und bei voraussichtlich nützlicher Trennschärfe gezielt nachfragen. Diese Auswahl kann algorithmisch erfolgen. Ein Chat-Modell könnte Anforderungen, Widersprüche und Antworten interpretieren oder Fragen formulieren. Die Fachlogik gehört ins Backend; das Frontend zeigt den Dialog. Grundsatz: nur fragen, wenn es das Ergebnis verbessert.
- **Zusammenfassung und Synthese:** Optional eine sehr kurze anfragebezogene Zusammenfassung je Treffer; später ausgewählte Originalstellen in ein eigenes Arbeitsdokument übernehmen. Aussagen müssen zum richtigen Geltungsbereich gehören und an den Quellen prüfbar bleiben.
- **Weitere Ressourcen:** HTML-Ordner, Markdown, DOCX, EPUB, Notebooks und LaTeX sowie KI-Modelle, Libraries, Datensätze und Papers. Darstellung und Analyse richten sich nach dem Ressourcentyp. Relevanzdimensionen könnten etwa Task-, Hardware- und Lizenz-Fit bei Modellen oder Funktion, Plattform und Wartungszustand bei Libraries umfassen; Evidenz liefern Originaldokumente, Model Cards, READMEs, Metadaten und Benchmarks.
- **Grob- und Feinsuche:** Große Bestände zuerst auf Bücher, Kapitel oder andere Kandidaten eingrenzen, danach Details durchsuchen. EPUB bietet dafür häufig bereits eine Kapitelstruktur. Ein grober dauerhafter Index könnte die aufwendige Feinsuche auf wenige Kandidaten begrenzen.

Diese Ideen bleiben als Richtung erhalten, ohne dafür im MVP zusätzliche Architektur vorzubereiten. Der aktuelle Name ist Info Retriever; DocNavi und ResourceRetriever waren frühere Namen.
