"""Convert the sample paper with picture export and formula recognition."""

import logging
import re
from pathlib import Path
from time import perf_counter
from urllib.parse import quote

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode


def export_markdown(document, path):
    image_dir = path.parent / f"{path.stem}_artifacts"
    markdown = document.export_to_markdown(
        image_mode=ImageRefMode.REFERENCED,
        image_dir=image_dir,
        image_uri_prefix=quote(image_dir.name) + "/",
    )
    # Model output can contain alignment markers (&) and multiple formula lines.
    markdown = re.sub(
        r"\$\$(.*?)\$\$",
        lambda match: "$$\n\\begin{aligned}\n" + match[1]
        + "\n\\end{aligned}\n$$",
        markdown,
        flags=re.DOTALL,
    )
    path.write_text(markdown, encoding="utf-8")


def main():
    logging.basicConfig(level=logging.INFO)
    experiment_dir = Path(__file__).resolve().parent
    source = experiment_dir.parents[1] / "data/sample_pdfs/Attention Is All You Need.pdf"
    if not source.is_file():
        raise FileNotFoundError(source)

    # Keep the baseline settings; add picture crops and formula-to-LaTeX recognition.
    options = PdfPipelineOptions(
        do_ocr=False,
        do_table_structure=True,
        generate_picture_images=True,
        images_scale=2.0,
        do_formula_enrichment=True,
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

    output_dir = experiment_dir / "output/experiment2"
    output_dir.mkdir(parents=True, exist_ok=True)
    document.save_as_json(output_dir / f"{source.stem}.json")
    export_markdown(document, output_dir / f"{source.stem}.md")
    formulas = [item for item in document.texts if item.label.value == "formula"]
    print(f"Converted {len(document.pages)} pages in {perf_counter() - started:.1f}s.")
    print(f"Pictures: {len(document.pictures)}; nonempty formulas: "
          f"{sum(bool(item.text.strip()) for item in formulas)}/{len(formulas)}")
    print(f"Results: {output_dir}")


if __name__ == "__main__":
    main()
