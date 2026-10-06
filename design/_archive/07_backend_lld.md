# Info Retriever – übergreifendes Backend-LLD

**Status: Entwurf – noch keine Freigabe zur Implementierung.**

## Ziel und Rahmen

Dieses LLD beschreibt die gemeinsame Backend-Struktur für die [MVP-Use-Cases](06_mvp_use_cases.md). Die folgenden Entwürfe zu den einzelnen Use Cases konkretisieren Verhalten, Schnittstellen und Tests. Die Implementierung erfolgt schrittweise nach dem jeweiligen Go.

Der MVP soll beim Experimentieren mit deutschen und englischen PDFs zeigen, wie hilfreich semantische Suche mit direkt prüfbaren Originalfundstellen ist. Eine erste Referenz ist die 104-seitige BDS-IPSC-Sportordnung. KI-Entwicklung zu lernen und die eingesetzten Werkzeuge zu verstehen ist ein wesentliches Projektziel.

## Architektur

```text
Browser: Oberfläche, PDF.js, fetch()
                 ↕ HTTP / JSON, PDF-Datei
api.py: FastAPI
                 ↓ Python-Aufrufe
service.py: übergreifende Koordination und Zustand
                 ↓
PDF-Verarbeitung · Embeddings · FAISS · Suche
```

- Das Python-Backend läuft lokal auf dem Notebook. Der Browser ist die Bedienoberfläche.
- Die Ablaufsteuerung ist fest programmiert. Der MVP benötigt weder KI-Agentensteuerung noch ein Chat-Modell.
- FAISS übernimmt die lokale Vektorsuche. Das Embedding-Modell läuft auf der CPU und wird über einen dünnen Adapter angebunden.
- Sentence Transformers mit PyTorch ist der vorgesehene Einstieg für lokale Embeddings. Das konkrete Modell ist noch offen; `multilingual-e5-small` ist ein Kandidat.
- FastAPI bildet die HTTP-Grenze. Das Frontend verwendet das eingebaute `fetch()`. Vorgesehen ist die Auslieferung von Frontend-Dateien und API über denselben lokalen Server.
- Der Backend-Kern bleibt unabhängig von HTTP und kann direkt aus pytest oder einem Notebook aufgerufen werden.

## Projektstruktur

```text
backend/
├── pyproject.toml
├── src/
│   └── info_retriever/
│       ├── __init__.py
│       ├── api.py           # HTTP-Endpunkte, Eingabeprüfung, Antworten
│       ├── service.py       # Use-Case-übergreifende Koordination und Zustand
│       ├── models.py        # Dokumentelemente, Fundstellen, Suchtreffer
│       ├── pdf.py           # UC 1: PDF laden und strukturieren
│       ├── embeddings.py    # UC 2: Schnittstelle und Modelladapter
│       ├── index.py         # UC 3: FAISS-Index aufbauen und durchsuchen
│       └── search.py        # UC 4: Anfrage einbetten, Treffer zusammenstellen
└── tests/
    ├── fixtures/            # Kleine Testdokumente und gemeinsame Testdaten
    ├── test_pdf.py
    ├── test_embeddings.py
    ├── test_index.py
    ├── test_search.py
    ├── test_service.py
    └── integration/         # Zusammenspiel realer Komponenten, API-Tests
```

Die Zuordnung von UC 1–4 zu den Fachmodulen bleibt erhalten. Bei UC 5 „Ausgewähltes Ergebnis im PDF-Viewer anzeigen“ übernimmt das Frontend Navigation und Markierung; das Backend liefert PDF und Fundstellendaten. Module und Tests entstehen schrittweise. `pyproject.toml` bündelt Paketdefinition, Abhängigkeiten und Testkonfiguration.

## Zuständigkeiten und Schnittstellen

### HTTP-Fassade und Service

| Modul | Verantwortung |
|---|---|
| `api.py` | Kennt FastAPI, prüft HTTP-Eingaben, delegiert an den Service und übersetzt Ergebnisse und Fehler in HTTP-Antworten. Enthält keine fachliche Ablaufsteuerung oder Zustandsverwaltung. |
| `service.py` | Koordiniert Use Cases und hält ihren gemeinsamen Zustand. Delegiert die einzelnen Verarbeitungsschritte an die Fachmodule. |
| `pdf.py`, `embeddings.py`, `index.py`, `search.py` | Implementieren die Verarbeitung der zugeordneten Use Cases. |

Service und Fachmodule kennen FastAPI nicht und sind direkt aus pytest oder einem Notebook aufrufbar. FastAPI-Typen bleiben in `api.py`.

Vorgesehene Methoden eines `InfoRetriever`-Objekts in `service.py`:

- `prepare_document(pdf_path) → DocumentInfo`: UC 1–3 verbinden: PDF analysieren, Embeddings berechnen, Index aufbauen.
- `search(document_id, query, limit) → list[SearchHit]`: Suche an `search.py` delegieren.
- `get_document(document_id) → Path`: Zugehöriges Original-PDF erschließen.

Konkrete HTTP-Endpunkte und Datentypen folgen in den Use-Case-Entwürfen. Der Browser übergibt eine PDF-Datei und verwendet anschließend deren Dokument-ID; interne Dateipfade sind nicht frei wählbar. Treffer enthalten bereits die Fundstellen für Navigation und Markierung im Viewer.

### Daten und Originalfundstellen

`models.py` beschreibt typisierte Dokumentelemente, Fundstellen und Treffer. Ein Dokumentelement hat eine eindeutige ID, Originaltext, eine Hierarchieebene und gegebenenfalls einen Verweis auf sein übergeordnetes Element. Seine Fundstellen enthalten Seiten- und Positionsdaten; mehrere Rechtecke und Seiten müssen darstellbar sein.

Die Zuordnung **Indexeintrag → Dokumentelement → Originalfundstelle** bleibt eindeutig. Für Embeddings ergänzter Kontext, etwa eine Überschrift, darf den Originaltext nicht ersetzen. Bei wiederkehrenden Regelnummern und ähnlichen Abschnitten darf keine Zuordnung allein über den Text erfolgen. Ein Suchscore beschreibt Ähnlichkeit, keine bestätigte Gültigkeit einer Aussage für den gesuchten Fall.

### Embedding-Adapter und FAISS

Die kleine Embedding-Schnittstelle bietet `embed_documents(texts)` und `embed_query(text)`. Ein Adapter übernimmt Modellaufruf, erforderliche Präfixe und einheitliche Vektornormalisierung. Er stellt außerdem Modellkennung, Vektordimension und Eingabelimit bereit. Der Adapter wird den verarbeitenden Funktionen beziehungsweise Objekten übergeben; Tests können einen einfachen Adapter mit festen Vektoren einsetzen. Ein Python-`Protocol` ist dafür vorgesehen, kein Plugin-System.

`index.py` kapselt FAISS und die Zuordnung der Vektoren zu Dokumentelementen. `search.py` verbindet Query-Embedding, Indexsuche und Ergebnisaufbereitung. Als einfacher Start ist exakte Suche mit `IndexFlatIP` über normalisierte Vektoren vorgesehen; das Skalarprodukt entspricht dann der Cosine Similarity.

Dokument- und Query-Embeddings müssen zum selben Modell und denselben Verarbeitungseinstellungen gehören. Ein Modellwechsel erfordert neue Dokument-Embeddings und einen neuen Index. Zu lange Eingaben dürfen nicht unbemerkt abgeschnitten werden; ihre Aufteilung ist Teil des UC-2-Entwurfs.

## Zustand und Fehler

Für den MVP ist ein lokaler Backend-Prozess mit einem aktiven PDF vorgesehen. Das `InfoRetriever`-Objekt in `service.py` verwaltet Modelladapter, Dokumentelemente und Index. Das Modell wird über mehrere Anfragen hinweg wiederverwendet. Ein Dokument wird erst nach vollständig erfolgreicher Aufbereitung als durchsuchbar bereitgestellt.

Fehler wie ein unlesbares PDF, fehlender zugänglicher Text oder ein unbekanntes Dokument werden an der öffentlichen Schnittstelle verständlich gemeldet. Der Umgang mit parallelen Aufrufen, dem Wechsel des aktiven PDFs und längeren Aufbereitungszeiten wird vor der HTTP-Implementierung konkretisiert. Dauerhafte Speicherung und Wiederherstellung sind noch offen.

## Tests und Vorgehen

Es gelten [AGENTS.md](../AGENTS.md) und die dort eingeordneten [Testregeln](how_to_test.md). Unit-Tests prüfen relevantes öffentlich beobachtbares Verhalten; private Hilfsfunktionen und triviale Weiterleitungen erhalten keine eigenen Pflichttests. Testmodule orientieren sich an den produktiven Modulen, Tests zu Klassen werden in entsprechenden Testklassen gebündelt.

- Kleine PDFs prüfen Extraktion, Hierarchie und Fundstellenzuordnung, insbesondere bei ähnlich formulierten Abschnitten mit unterschiedlichen Überschriften.
- Feste Vektoren prüfen Ranking und Zuordnung unabhängig vom Embedding-Modell. Integrationstests verwenden echtes FAISS und reale PDF-Verarbeitung.
- Service-Tests prüfen übergreifende Abläufe und Zustandswechsel direkt in Python, insbesondere dass eine fehlgeschlagene Aufbereitung keinen halbfertigen Dokumentzustand veröffentlicht.
- Tests mit dem echten Embedding-Modell laufen gesondert; schnelle Tests benötigen keinen Modelldownload. HTTP-Verhalten wird mit pytest und FastAPIs `TestClient` unter `tests/integration` geprüft, ohne separat gestarteten Webserver.
- Die Suchqualität wird zusätzlich mit repräsentativen Fragen und erwarteten Fundstellen beurteilt. Die korrekte Markierung wird später mit PDF.js einschließlich Zoom und Seitengeometrie geprüft.

Wir implementieren zuerst den Python-Kern mit pytest, anschließend die HTTP-Anbindung und später das Frontend. Die übergreifende Struktur wird durch kleine Entwürfe pro Use Case konkretisiert, nicht vorab als leeres Framework angelegt.

## Offene Entscheidungen für die folgenden Entwürfe

- UC 1: Docling konkret einsetzen; Hierarchieerkennung und deren Grenzen, Satzzerlegung sowie Seitenzählung und Koordinatenkonvention festlegen.
- UC 2: Startmodell auswählen und lange Abschnitte auf mehreren Hierarchieebenen behandeln.
- UC 3: Lebensdauer des Index und gegebenenfalls dauerhafte Speicherung einschließlich Modell- und Verarbeitungskennung festlegen.
- UC 4: Treffer verschiedener Ebenen zusammenführen und Überschneidungen behandeln; keine einstellbare mehrdimensionale Gewichtung im MVP.
- HTTP / UC 5: Request- und Response-Daten, Fehlerfälle, Upload-Lebensdauer, laufende Verarbeitung und die Übergabe der Markierungsdaten an den Viewer festlegen.

