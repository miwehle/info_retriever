"""Inspect Marker's native section assignments for the IPSC handbook on CPU."""

import os
from pathlib import Path
from time import perf_counter

EXPERIMENT_DIR = Path(__file__).resolve().parent
ROOT = EXPERIMENT_DIR.parents[1]
# Set before importing Marker/Surya, which load their settings during import.
os.environ["TORCH_DEVICE"] = "cpu"
os.environ["FAST_DETECTOR_DEVICE"] = "cpu"
os.environ.setdefault("HF_HOME", str(ROOT / ".cache/huggingface"))
os.environ.setdefault("MODEL_CACHE_DIR", str(ROOT / ".cache/marker"))

from bs4 import BeautifulSoup
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict, shutdown_models
from marker.output import save_output
from marker.renderers.json import JSONRenderer
from marker.renderers.markdown import MarkdownRenderer
from marker.schema import BlockTypes


def write_structure_report(document, rendered, output_dir, processing="CPU, fast, OCR und LLM ausgeschaltet"):
    """Show native output nesting separately from logical section assignments."""
    lines = []
    headings = []
    known_ids = set()
    references = set()

    def visit(block, depth, parent):
        known_ids.add(block.id)
        hierarchy = block.section_hierarchy or {}
        references.update(hierarchy.values())
        text = " ".join(BeautifulSoup(block.html, "html.parser").get_text(" ").split())
        lines.append(
            f"{'  ' * depth}{block.id} [{block.block_type}; "
            f"section_hierarchy={hierarchy}] {text[:120]}"
        )
        if block.block_type == str(BlockTypes.SectionHeader):
            headings.append((block, parent, text))
        for child in block.children or []:
            visit(child, depth + 1, block.id)

    for page in rendered.children:
        visit(page, 0, "Document")
    if missing := references - known_ids:
        raise ValueError(f"Section references absent from rendered output: {missing}")
    (output_dir / "tree.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    native_headings = {
        str(h.id): h for h in document.contained_blocks((BlockTypes.SectionHeader,))
    }
    report = [
        "# Marker: Struktur der Sportordnung", "",
        f"{len(document.pages)} Seiten, {len(headings)} gerenderte Überschriften. {processing}.", "",
        "tree.txt zeigt die native Verschachtelung der JSON-Ausgabe; section_hierarchy zeigt zusätzlich die logische Abschnittszuordnung. Der Bericht konstruiert keinen eigenen Kapitelbaum und verändert keine Level. Texte in tree.txt sind auf 120 Zeichen gekürzt; JSON und Markdown enthalten die vollständige Ausgabe.", "",
        "PDF-Seiten werden hier ab 1 gezählt; Marker-IDs enthalten Seitenindizes ab 0. section_hierarchy kann die jeweilige Überschrift selbst enthalten und ist keine direkte Elternreferenz.", "",
        "| PDF-Seite | Überschrift | Level | ID | JSON-Elternknoten | section_hierarchy |",
        "|---|---|---|---|---|---|",
    ]
    for block, parent, text in headings:
        native = native_headings[block.id]
        text = text.replace("|", "\\|")
        report.append(
            f"| {native.page_id + 1} | {text} | {native.heading_level} | "
            f"`{block.id}` | `{parent}` | `{block.section_hierarchy}` |"
        )
    (output_dir / "structure.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main():
    source = ROOT / "data/sample_pdfs/bds_sportordnung_ipsc_kurzwaffe.pdf"
    if not source.is_file():
        raise FileNotFoundError(source)
    output_dir = EXPERIMENT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    # Avoid spawning extra Python processes for text extraction on Windows.
    config = {"mode": "fast", "disable_ocr": True, "use_llm": False, "pdftext_workers": 1}
    started = perf_counter()
    print("Loading Marker; converting the handbook on CPU...", flush=True)
    models = create_model_dict()
    try:
        converter = PdfConverter(artifact_dict=models, config=config)
        document = converter.build_document(str(source))
        rendered = JSONRenderer(config)(document)
        save_output(rendered, str(output_dir), source.stem)
        save_output(MarkdownRenderer(config)(document), str(output_dir), source.stem)
        write_structure_report(document, rendered, output_dir)
        print(f"Converted {len(document.pages)} pages in {perf_counter() - started:.1f}s.")
        print(f"Results: {output_dir}")
    finally:
        shutdown_models(models)


if __name__ == "__main__":
    main()
