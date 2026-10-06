"""Convert the IPSC handbook, preserving pictures and formulas as PDF crops."""

import logging
from pathlib import Path
from time import perf_counter

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.serializer.markdown import MarkdownDocSerializer
from docling_core.types.doc import FormulaItem, ImageRefMode

from convert3 import FormulaCropSerializer, PictureCropSerializer


def main():
    logging.basicConfig(level=logging.INFO)
    experiment_dir = Path(__file__).resolve().parent
    source = experiment_dir.parents[1] / "data/sample_pdfs/bds_sportordnung_ipsc_kurzwaffe.pdf"
    options = PdfPipelineOptions(
        do_ocr=False, do_table_structure=True, do_formula_enrichment=False,
        generate_page_images=True, images_scale=2.0,
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
    output_dir = experiment_dir / "output/experiment4"
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
    print(f"Converted {len(document.pages)} pages in {perf_counter() - started:.1f}s.")
    print(f"Pictures: {len(document.pictures)}; "
          f"formula regions: {sum(isinstance(t, FormulaItem) for t in document.texts)}; "
          f"tables: {len(document.tables)}")
    print(f"Results: {output_dir}")


if __name__ == "__main__":
    main()
