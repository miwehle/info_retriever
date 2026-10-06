"""Correct only Marker's heading levels with OpenAI and compare before/after."""

import json
import os
import re
from time import perf_counter

from dotenv import load_dotenv

from convert import (
    ROOT, EXPERIMENT_DIR, BeautifulSoup, BlockTypes, JSONRenderer,
    MarkdownRenderer, PdfConverter, create_model_dict, save_output,
    shutdown_models, write_structure_report,
)
from marker.processors.llm.llm_sectionheader import LLMSectionHeaderProcessor
from marker.services.openai import OpenAIService

MODEL = "gpt-5-mini"


def correct_headings(document, api_key, output_dir):
    """Use Marker's prompt/service; permit only level changes to known headings."""
    service = OpenAIService({
        "openai_model": MODEL, "openai_api_key": api_key,
        "timeout": 180, "max_retries": 0,
    })
    processor = LLMSectionHeaderProcessor(service, {"use_llm": True})
    selected = [
        (block, processor.normalize_block_json(block, document, page))
        for page in document.pages
        for block in page.structure_blocks(document)
        if block.block_type == BlockTypes.SectionHeader
        and not block.ignore_for_output
    ]
    if not selected:
        raise RuntimeError("No nonempty headings found for correction.")
    original = {str(block.id): (block, data["html"], block.heading_level)
                for block, data in selected}
    original_html = {ref: block.html for ref, (block, _, _) in original.items()}
    levels = {}
    discarded_edits = []

    def checked_service(prompt, image, block, schema):
        # The built-in heading processor sends text only, not the PDF or images.
        if image is not None:
            raise ValueError("This experiment sends headings only.")
        (output_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        response = service(prompt, None, block, schema)
        if not response or response.get("correction_type") not in {
            "no_corrections", "corrections_needed"
        }:
            raise RuntimeError("OpenAI heading correction failed; no corrected export written.")
        (output_dir / "response.json").write_text(
            json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if response["correction_type"] == "no_corrections":
            if response.get("blocks"):
                raise ValueError("Contradictory response: no_corrections with changed blocks.")
            return response
        if not response.get("blocks"):
            raise ValueError("Correction requested but no changed blocks returned.")
        for change in response["blocks"]:
            ref, html = change["id"], change["html"]
            if ref not in original or ref in levels:
                raise ValueError(f"Unknown or duplicate heading: {ref}")
            match = re.fullmatch(r"<h([1-6])\b[^>]*>.*</h\1>", html.strip(), re.DOTALL)
            if not match:
                raise ValueError(f"Invalid heading level markup: {ref}")
            # Take only the level. Never copy generated text/markup into the source.
            normalize = lambda value: " ".join(re.sub(r"(<\/?h)[1-6]\b", r"\1N", value).split())
            if normalize(html) != normalize(original[ref][1]):
                discarded_edits.append(ref)
            levels[ref] = int(match.group(1))
            change["html"] = re.sub(
                r"(<\/?h)[1-6]\b", lambda tag: tag[1] + match[1], original[ref][1]
            )
        return response

    processor.llm_service = checked_service
    # Call directly so errors are not swallowed by the processor's __call__.
    processor.process_rewriting(document, selected)
    for ref, level in levels.items():
        original[ref][0].heading_level = level
        # Preserve native rendering, including source anchors (Marker otherwise duplicates them).
        original[ref][0].html = original_html[ref]

    report = [
        "# Überschriftenvergleich", "",
        f"Modell: `{MODEL}`. {len(selected)} Überschriften übergeben; "
        f"{sum(original[ref][2] != level for ref, level in levels.items())} Level geändert.", "",
        f"Bei {len(discarded_edits)} Vorschlägen wurden zusätzliche Text-/Markupänderungen verworfen. Übernommen werden ausschließlich Level; Originaltext und Markup bleiben erhalten. Betroffene IDs: {', '.join(discarded_edits) or 'keine'}.", "",
        "Vorher und nachher beziehen sich auf denselben lokalen Konvertierungslauf. Leere/ignorierte Überschriften werden nicht an das LLM gesendet. Die Korrektur ergänzt keine fehlenden Überschriften.", "",
        "| PDF-Seite | Überschrift | Vorher | Nachher | ID |",
        "|---|---|---|---|---|",
    ]
    for ref, (block, html, old_level) in original.items():
        title = " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split()).replace("|", "\\|")
        report.append(f"| {block.page_id + 1} | {title} | {old_level} | {block.heading_level} | `{ref}` |")
    (output_dir / "comparison.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main():
    load_dotenv(ROOT / ".env", override=False)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY fehlt. Als Umgebungsvariable oder in der lokalen .env setzen.")
    source = ROOT / "data/sample_pdfs/bds_sportordnung_ipsc_kurzwaffe.pdf"
    output_dir = EXPERIMENT_DIR / "output/experiment2"
    output_dir.mkdir(parents=True, exist_ok=True)
    config = {"mode": "fast", "disable_ocr": True, "use_llm": False, "pdftext_workers": 1}
    started = perf_counter()
    models = create_model_dict()
    try:
        print("Converting PDF locally on CPU...", flush=True)
        document = PdfConverter(artifact_dict=models, config=config).build_document(str(source))
        local_seconds = perf_counter() - started
        save_output(JSONRenderer(config)(document), str(output_dir), "before")
        print(f"Local conversion: {local_seconds:.1f}s. Correcting headings with {MODEL}...", flush=True)
        correction_start = perf_counter()
        correct_headings(document, api_key, output_dir)
        correction_seconds = perf_counter() - correction_start
        rendered = JSONRenderer(config)(document)
        save_output(rendered, str(output_dir), source.stem)
        save_output(MarkdownRenderer(config)(document), str(output_dir), source.stem)
        write_structure_report(document, rendered, output_dir, f"CPU, fast, OCR aus; Überschriftenkorrektur mit {MODEL}")
        (output_dir / "timing.json").write_text(json.dumps({
            "model": MODEL, "local_seconds": local_seconds,
            "correction_seconds": correction_seconds,
            "total_seconds_without_imports": perf_counter() - started,
        }, indent=2), encoding="utf-8")
        print(f"Heading correction: {correction_seconds:.1f}s. Results: {output_dir}")
    finally:
        shutdown_models(models)


if __name__ == "__main__":
    main()
