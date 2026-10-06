"""Export pictures and detected formulas as original PDF crops, without transcription."""

import logging
import os
from pathlib import Path
from time import perf_counter
from urllib.parse import quote

from pydantic import BaseModel

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.serializer.common import create_ser_result
from docling_core.transforms.serializer.markdown import (
    MarkdownDocSerializer, MarkdownPictureSerializer, MarkdownTextSerializer,
)
from docling_core.types.doc import FormulaItem, ImageRefMode


def crop_markdown(item, doc, output_dir, source):
    """Keep one crop and source-page link per detected region."""
    image_dir = output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    source_link = quote(Path(os.path.relpath(source, output_dir)).as_posix())
    parts = []
    for index, provenance in enumerate(item.prov):
        image = item.get_image(doc=doc, prov_index=index)
        if image is None:
            raise ValueError(f"No page image for {item.self_ref}")
        filename = f"{item.self_ref.strip('#/').replace('/', '_')}_{index}.png"
        image.save(image_dir / filename)
        page = provenance.page_no
        parts.append(
            f"![{item.label.value}, PDF-Seite {page}](images/{filename})\n\n"
            f"[Quelle: {source.name}, PDF-Seite {page}]({source_link}#page={page})"
        )
    if not parts:
        raise ValueError(f"No source location for {item.self_ref}")
    return "\n\n".join(parts)


class FormulaCropSerializer(MarkdownTextSerializer):
    output_dir: Path
    source: Path

    def serialize(self, *, item, doc, **kwargs):
        if isinstance(item, FormulaItem):
            return create_ser_result(
                text=crop_markdown(item, doc, self.output_dir, self.source),
                span_source=item,
            )
        return super().serialize(item=item, doc=doc, **kwargs)


class PictureCropSerializer(BaseModel, MarkdownPictureSerializer):
    output_dir: Path
    source: Path

    def serialize(self, *, item, doc, doc_serializer, **kwargs):
        text = crop_markdown(item, doc, self.output_dir, self.source)
        caption = doc_serializer.serialize_captions(item=item, **kwargs).text
        return create_ser_result(text=f"{text}\n\n{caption}", span_source=item)


def main():
    logging.basicConfig(level=logging.INFO)
    experiment_dir = Path(__file__).resolve().parent
    source = experiment_dir.parents[1] / "data/sample_pdfs/Attention Is All You Need.pdf"
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
    output_dir = experiment_dir / "output/experiment3"
    output_dir.mkdir(parents=True, exist_ok=True)
    serializer = MarkdownDocSerializer(
        doc=document,
        text_serializer=FormulaCropSerializer(output_dir=output_dir, source=source),
        picture_serializer=PictureCropSerializer(output_dir=output_dir, source=source),
    )
    (output_dir / f"{source.stem}.md").write_text(
        serializer.serialize().text, encoding="utf-8"
    )
    # Keep coordinates and content in JSON, without embedding all rendered PDF pages.
    document.save_as_json(output_dir / f"{source.stem}.json", image_mode=ImageRefMode.PLACEHOLDER)
    print(f"Converted {len(document.pages)} pages in {perf_counter() - started:.1f}s.")
    print(f"Results: {output_dir}")


if __name__ == "__main__":
    main()
