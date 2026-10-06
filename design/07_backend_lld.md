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
service.py: InfoRetriever-Fassade
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
│       ├── service.py       # InfoRetriever-Fassade und Ablaufsteuerung
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

Die Struktur ist eine Orientierung; Module und Tests entstehen erst, wenn sie im jeweiligen Schritt benötigt werden. Ein Modul pro Use Case ist keine Pflicht. Funktionen genügen, solange Klassen keinen konkreten Vorteil für Zustand oder Schnittstellen bieten. `pyproject.toml` bündelt Paketdefinition, Abhängigkeiten und Testkonfiguration.

## Zuständigkeiten und Schnittstellen

### Fassade und HTTP-Anbindung

Die Fassade verbindet die Verarbeitungsschritte und verwaltet den vorbereiteten Dokumentzustand. Sie verbirgt diese Aufgaben hinter einer kleinen Python-API; sie ist keine zusätzliche Schicht aus bloßen Weiterleitungen. Vorgeschlagene Operationen:

```text
prepare_document(pdf_path) → DocumentInfo
search(document_id, query, limit) → list[SearchHit]
get_document(document_id) → Path
```

`prepare_document()` führt UC 1–3 aus: PDF analysieren, Embeddings berechnen, Index aufbauen. Diese Schritte bleiben intern einzeln prüfbar. `search()` liefert Originaltext, Score und Fundstellen für UC 4–5. `get_document()` erschließt das zugehörige Original-PDF. Die Namen und genauen Typen werden in den Use-Case-Entwürfen konkretisiert.

Die HTTP-Schicht nimmt einen Datei-Upload beziehungsweise eine Suchanfrage entgegen, prüft die Eingaben und übersetzt Fassadenergebnisse und Fehler in HTTP-Antworten. Ein interner Dateipfad ist kein vom Browser frei wählbarer Zugriffspfad. PDF-Dateien werden über ihre Dokument-ID bereitgestellt. Für die Auswahl eines bereits gelieferten Treffers ist normalerweise kein erneuter Suchaufruf nötig; Navigation und Hervorhebung übernimmt das Frontend.

### Daten und Originalfundstellen

`models.py` beschreibt typisierte Dokumentelemente, Fundstellen und Treffer. Ein Dokumentelement hat eine eindeutige ID, Originaltext, eine Hierarchieebene und gegebenenfalls einen Verweis auf sein übergeordnetes Element. Seine Fundstellen enthalten Seiten- und Positionsdaten; mehrere Rechtecke und Seiten müssen darstellbar sein.

Die Zuordnung **Indexeintrag → Dokumentelement → Originalfundstelle** bleibt eindeutig. Für Embeddings ergänzter Kontext, etwa eine Überschrift, darf den Originaltext nicht ersetzen. Bei wiederkehrenden Regelnummern und ähnlichen Abschnitten darf keine Zuordnung allein über den Text erfolgen. Ein Suchscore beschreibt Ähnlichkeit, keine bestätigte Gültigkeit einer Aussage für den gesuchten Fall.

### Embedding-Adapter und FAISS

Die kleine Embedding-Schnittstelle bietet `embed_documents(texts)` und `embed_query(text)`. Ein Adapter übernimmt Modellaufruf, erforderliche Präfixe und einheitliche Vektornormalisierung. Er stellt außerdem Modellkennung, Vektordimension und Eingabelimit bereit. Die Abhängigkeit wird beim Erzeugen der Fassade übergeben; Tests können einen einfachen Adapter mit festen Vektoren einsetzen. Ein Python-`Protocol` ist dafür vorgesehen, kein Plugin-System.

`index.py` kapselt FAISS und die Zuordnung der Vektoren zu Dokumentelementen. `search.py` verbindet Query-Embedding, Indexsuche und Ergebnisaufbereitung. Als einfacher Start ist exakte Suche mit `IndexFlatIP` über normalisierte Vektoren vorgesehen; das Skalarprodukt entspricht dann der Cosine Similarity.

Dokument- und Query-Embeddings müssen zum selben Modell und denselben Verarbeitungseinstellungen gehören. Ein Modellwechsel erfordert neue Dokument-Embeddings und einen neuen Index. Zu lange Eingaben dürfen nicht unbemerkt abgeschnitten werden; ihre Aufteilung ist Teil des UC-2-Entwurfs.

## Zustand und Fehler

Für den MVP ist zunächst ein lokaler Backend-Prozess mit einem aktiven PDF vorgesehen. Die Backend-Instanz hält Modell, Dokumentelemente und Index; das Modell wird über mehrere Anfragen hinweg wiederverwendet. Ein neues Dokument gilt erst nach vollständig erfolgreicher Aufbereitung als durchsuchbar. Suchaufrufe dürfen keinen halbfertigen Index sehen.

Fehler wie ein unlesbares PDF, fehlender zugänglicher Text oder ein unbekanntes Dokument werden an der öffentlichen Schnittstelle verständlich gemeldet. Der Umgang mit parallelen Aufrufen, dem Wechsel des aktiven PDFs und längeren Aufbereitungszeiten wird vor der HTTP-Implementierung konkretisiert. Dauerhafte Speicherung und Wiederherstellung sind noch offen.

## Tests und Vorgehen

Es gelten [AGENTS.md](../AGENTS.md) und die dort eingeordneten [Testregeln](how_to_test.md). Unit-Tests prüfen relevantes öffentlich beobachtbares Verhalten; private Hilfsfunktionen und triviale Weiterleitungen erhalten keine eigenen Pflichttests. Testmodule orientieren sich an den produktiven Modulen, Tests zu Klassen werden in entsprechenden Testklassen gebündelt.

- Kleine PDFs prüfen Extraktion, Hierarchie und Fundstellenzuordnung, insbesondere bei ähnlich formulierten Abschnitten mit unterschiedlichen Überschriften.
- Feste Vektoren prüfen Ranking und Zuordnung unabhängig vom Embedding-Modell. Integrationstests verwenden echtes FAISS und reale PDF-Verarbeitung.
- Tests mit dem echten Embedding-Modell laufen gesondert; schnelle Tests benötigen keinen Modelldownload. Die spätere HTTP-Schicht wird mit FastAPIs `TestClient` geprüft.
- Die Suchqualität wird zusätzlich mit repräsentativen Fragen und erwarteten Fundstellen beurteilt. Die korrekte Markierung wird später mit PDF.js einschließlich Zoom und Seitengeometrie geprüft.

Wir implementieren zuerst den Python-Kern mit pytest, anschließend die HTTP-Anbindung und später das Frontend. Die übergreifende Struktur wird durch kleine Entwürfe pro Use Case konkretisiert, nicht vorab als leeres Framework angelegt.

## Offene Entscheidungen für die folgenden Entwürfe

- UC 1: Docling konkret einsetzen; Hierarchieerkennung und deren Grenzen, Satzzerlegung sowie Seitenzählung und Koordinatenkonvention festlegen.
- UC 2: Startmodell auswählen und lange Abschnitte auf mehreren Hierarchieebenen behandeln.
- UC 3: Lebensdauer des Index und gegebenenfalls dauerhafte Speicherung einschließlich Modell- und Verarbeitungskennung festlegen.
- UC 4: Treffer verschiedener Ebenen zusammenführen und Überschneidungen behandeln; keine einstellbare mehrdimensionale Gewichtung im MVP.
- HTTP / UC 5: Request- und Response-Daten, Fehlerfälle, Upload-Lebensdauer, laufende Verarbeitung und die Übergabe der Markierungsdaten an den Viewer festlegen.

Die hier festgehaltenen späteren Entscheidungen ergänzen den bisherigen Entwurf: FAISS gehört zum MVP, die Embedding-Anbindung ist austauschbar, die Ausführung erfolgt lokal auf der CPU und FastAPI verbindet Browser und Backend. Ältere optionale Cloud- oder Agentenüberlegungen sind nicht Teil dieses Umsetzungsvorschlags.
