"""Convert the sample paper into a DoclingDocument and readable Markdown."""

import json
import logging
from pathlib import Path
from time import perf_counter

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


def main():
    logging.basicConfig(level=logging.INFO)
    experiment_dir = Path(__file__).resolve().parent
    source = experiment_dir.parents[1] / "data/sample_pdfs/Attention Is All You Need.pdf"
    if not source.is_file():
        raise FileNotFoundError(source)

    # This paper contains embedded text; OCR is unnecessary for this experiment.
    options = PdfPipelineOptions(do_ocr=False, do_table_structure=True)
    options.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CPU)
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )

    started = perf_counter()
    result = converter.convert(source)
    if result.status != ConversionStatus.SUCCESS:
        raise RuntimeError(f"Conversion incomplete: {result.status}; {result.errors}")
    document = result.document

    output_dir = experiment_dir / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / f"{source.stem}.json").write_text(
        json.dumps(document.export_to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / f"{source.stem}.md").write_text(
        document.export_to_markdown(), encoding="utf-8"
    )
    print(f"Converted {len(document.pages)} pages in {perf_counter() - started:.1f}s.")
    print(f"Results: {output_dir}")
    print("\nDetected headings (not necessarily chapter hierarchy):")
    for item, _depth in document.iterate_items():
        if item.label.value in {"title", "section_header"}:
            pages = ", ".join(str(prov.page_no) for prov in item.prov)
            print(f"  Page {pages}: {item.text}")


if __name__ == "__main__":
    main()
