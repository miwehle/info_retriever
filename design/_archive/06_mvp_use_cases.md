# Info Retriever – MVP-Use-Cases

## Ziel und Umfang

Der MVP dient dazu, mit einem textbasierten PDF zu experimentieren: Wie gut hilft semantische Suche dabei, Informationen zu finden und direkt im Originalkontext zu prüfen?

Der Kernablauf ist: **PDF laden → Embeddings berechnen → FAISS-Index aufbauen → Anfrage stellen → Treffer auswählen → Originalfundstelle anzeigen.**

Die folgenden Use Cases umfassen Benutzeraktionen und interne Verarbeitungsschritte. Die Nummerierung beschreibt den Ablauf, nicht fünf getrennte Bedienaktionen.

## UC 1 – PDF laden

- **Eingabe:** Eine textbasierte PDF-Datei.
- **Ablauf:** Das PDF wird geladen; Text und erkennbare Dokumentstruktur werden extrahiert. Die Verbindung der extrahierten Inhalte zu ihren Originalfundstellen bleibt erhalten.
- **Ergebnis:** Der PDF-Inhalt steht für die weitere Verarbeitung bereit. Nicht lesbare oder nicht unterstützte Dateien werden verständlich gemeldet. OCR gehört nicht zum MVP.

## UC 2 – Embeddings für den PDF-Inhalt ermitteln

- **Voraussetzung:** Das PDF wurde geladen und analysiert.
- **Ablauf:** Für Inhalte auf mehreren hierarchischen Ebenen werden Embeddings berechnet: Kapitel, Unterkapitel, Absätze und Sätze, soweit diese Ebenen ermittelt werden können.
- **Ergebnis:** Die Embeddings sind ihren Textelementen, Hierarchieebenen und Originalfundstellen eindeutig zugeordnet.
- **Offen:** Auswahl des Embedding-Modells sowie Umgang mit langen Abschnitten und nicht zuverlässig erkennbarer Hierarchie.

## UC 3 – Embeddings in einem FAISS-Index speichern

- **Voraussetzung:** Die Embeddings liegen vor.
- **Ablauf:** Die Embeddings werden in einen FAISS-Index aufgenommen. Die Zuordnung zwischen Indexeinträgen und Dokumentelementen bleibt erhalten.
- **Ergebnis:** Ein durchsuchbarer Index für das geladene PDF. Eine dauerhafte Speicherung über Programmstarts hinweg ist noch nicht festgelegt.

## UC 4 – Ergebnisse zu einer Suchanfrage ermitteln

- **Eingabe:** Eine natürlichsprachliche Anfrage, typischerweise eine Frage, zum geladenen PDF.
- **Voraussetzung:** Der FAISS-Index ist bereit.
- **Ablauf:** Für die Anfrage wird ein zum Dokumentindex kompatibles Embedding erzeugt. FAISS ermittelt ähnliche Dokumentelemente.
- **Ergebnis:** Eine nach Relevanz sortierte Trefferliste mit Originaltext, Relevanzwert, Hierarchiezuordnung und Fundstellendaten. Text und Fundstelle gehören stets zum selben Dokumentelement.
- **Offen:** Wie Treffer der verschiedenen Hierarchieebenen in der Ergebnisliste zusammengeführt werden. Eine einstellbare mehrdimensionale Gewichtung gehört zunächst nicht zum MVP.

## UC 5 – Ausgewähltes Ergebnis im PDF-Viewer anzeigen

- **Eingabe:** Der Benutzer wählt einen Treffer aus der Ergebnisliste in der KI-Seitenleiste.
- **Ablauf:** Der PDF-Viewer navigiert zur Originalfundstelle und hebt die zugehörige Passage hervor.
- **Ergebnis:** Der Benutzer kann den Treffer im Originalkontext prüfen und im PDF weiterblättern.
- **Backend-Anteil:** Eindeutige Zuordnung zum PDF sowie Seiten- und Positionsdaten bereitstellen. Darstellung, Navigation und Hervorhebung übernimmt später das Frontend.

## Nicht im MVP

- KI-generierte Zusammenfassungen und Synthese.
- Mehrstufiger Dialog mit intelligenten Rückfragen.
- Einstellbare Gewichtung mehrerer Relevanzdimensionen.
- Weitere Ressourcentypen und OCR.

## Prüfung

Automatisierte Backend-Tests mit pytest prüfen insbesondere die Zuordnung von Text, Hierarchie, Indexeintrag und Originalfundstelle sowie Suche und Ranking. Die korrekte Markierung wird später im Zusammenspiel mit dem Viewer geprüft. Den praktischen Nutzen beurteilen wir anhand echter PDFs und eigener Suchfragen.

## Einordnung in den bisherigen Entwurf

Diese Datei beschreibt den gemeinsam präzisierten MVP-Umfang. FAISS und Embeddings auf mehreren Hierarchieebenen gehören dazu; ältere Aussagen in den Design-Dateien, die FAISS zurückstellen, sind damit überholt. Ein Use-Case-Diagramm im draw.io-Format kann später ergänzt werden.
