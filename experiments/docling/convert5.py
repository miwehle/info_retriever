"""Test Docling heading inference and expose the actual document tree."""

import logging
from collections import Counter
from pathlib import Path
from time import perf_counter

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import HeadingHierarchyOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.serializer.markdown import MarkdownDocSerializer
from docling_core.types.doc import FormulaItem, ImageRefMode

from convert3 import FormulaCropSerializer, PictureCropSerializer

def write_structure_report(document, output_dir):
    """Report native relationships without constructing an artificial chapter tree."""
    lines = []
    depths = []
    for root in (document.body, document.furniture):
        def visit(item, depth):
            depths.append(depth)
            text = " ".join(getattr(item, "text", getattr(item, "name", "")).split())
            level = getattr(item, "level", None)
            label = getattr(item, "label", "root")
            label = getattr(label, "value", label)
            pages = sorted({p.page_no for p in getattr(item, "prov", [])})
            details = f"level={level}; " if level is not None else ""
            lines.append(f"{'  ' * depth}{item.self_ref} [{label}; {details}pages={pages}] {text[:120]}")
            for child in item.children:
                visit(child.resolve(document), depth + 1)
        visit(root, 0)
    (output_dir / "tree.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    headings = [t for t in document.texts if t.label.value == "section_header"]
    nested = sum(h.parent.resolve(document).label.value == "section_header" for h in headings if h.parent)
    report = [
        "# Experiment 5: Strukturprüfung", "",
        "Doclings Ebenenerkennung ist aktiviert (Lesezeichen, Nummerierung und Schriftmerkmale). Kein eigener Umbau des Baums.", "",
        f"- Direkte Kinder von body: {len(document.body.children)}",
        f"- Maximale Baumtiefe unter den Wurzeln: {max(depths, default=0)}",
        f"- Überschriften je level: {dict(sorted(Counter(h.level for h in headings).items()))}",
        f"- Überschriften mit einer Überschrift als direktem Elternknoten: {nested}/{len(headings)}", "",
        "Der tatsächliche Baum steht in [tree.txt](tree.txt). Ein unterschiedlicher level-Wert belegt noch keine Eltern-Kind-Verschachtelung.", "",
        "## Erkannte Überschriften", "",
        "| PDF-Seite | Überschrift | level | Knoten | Elternknoten |",
        "|---|---|---|---|---|",
    ]
    for h in headings:
        title = " ".join(h.text.split()).replace("|", "\\|")
        pages = ", ".join(str(p.page_no) for p in h.prov)
        report.append(f"| {pages} | {title} | {h.level} | `{h.self_ref}` | `{h.parent.cref if h.parent else '- '}` |")
    (output_dir / "structure.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main():
    logging.basicConfig(level=logging.INFO)
    experiment_dir = Path(__file__).resolve().parent
    source = experiment_dir.parents[1] / "data/sample_pdfs/bds_sportordnung_ipsc_kurzwaffe.pdf"
    options = PdfPipelineOptions(
        do_ocr=False, do_table_structure=True, do_formula_enrichment=False,
        generate_page_images=True, images_scale=2.0,
        generate_parsed_pages=True,
        heading_hierarchy_options=HeadingHierarchyOptions(enabled=True),
    )
    options.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CPU)
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )
    started = perf_counter()
    result = converter.convert(source)
    if result.status != ConversionStatus.SUCCESS:
        raise RuntimeError(f"Conversion incomplete: {result.status}; {result.errors}")
    document = result.document
    output_dir = experiment_dir / "output/experiment5"
    output_dir.mkdir(parents=True, exist_ok=True)
    serializer = MarkdownDocSerializer(
        doc=document,
        text_serializer=FormulaCropSerializer(output_dir=output_dir, source=source),
        picture_serializer=PictureCropSerializer(output_dir=output_dir, source=source),
    )
    (output_dir / f"{source.stem}.md").write_text(
        serializer.serialize().text, encoding="utf-8"
    )
    document.save_as_json(
        output_dir / f"{source.stem}.json", image_mode=ImageRefMode.PLACEHOLDER
    )
    write_structure_report(document, output_dir)
    print(f"Converted {len(document.pages)} pages in {perf_counter() - started:.1f}s.")
    print(f"Pictures: {len(document.pictures)}; "
          f"formula regions: {sum(isinstance(t, FormulaItem) for t in document.texts)}; "
          f"tables: {len(document.tables)}")
    print(f"Results: {output_dir}")


if __name__ == "__main__":
    main()
