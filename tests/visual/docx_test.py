#!/usr/bin/env python3

"""Regression test for DOCX generation.

Runs screenplain on each .fountain file in the given directory,
generating a DOCX file and comparing its structure to the corresponding
reference DOCX file.

If no reference DOCX file exists, one is created from the current output.
"""

import shutil
import sys
import tempfile
from pathlib import Path

import screenplain.main
from tests.docx_reader import Document, Paragraph, Table


def _extract_structure(doc):
    """Extract a comparable structure from a DOCX document."""
    items = []
    for item in doc.body_items:
        if isinstance(item, Paragraph):
            items.append(
                {
                    "paragraph": {
                        "style": item.style_name,
                        "text": item.text,
                        "runs": [
                            {
                                "text": r.text,
                                "bold": r.bold,
                                "italic": r.italic,
                                "underline": r.underline,
                            }
                            for r in item.runs
                            if r.text
                        ],
                    }
                }
            )
        elif isinstance(item, Table):
            items.append(
                {
                    "table": [
                        [
                            [
                                {"style": p.style_name, "text": p.text}
                                for p in cell.paragraphs
                            ]
                            for cell in row.cells
                        ]
                        for row in item.rows
                    ]
                }
            )
    return items


FILES_DIR = Path(__file__).resolve().parent.parent / "files"


def test_docx_output_matches_references():
    """Collected by pytest so the DOCX reference fixtures are actually
    exercised in CI (not only via the __main__ runner below)."""
    assert compare(FILES_DIR), "DOCX output diverged from reference fixtures"


def compare(directory) -> bool:
    reference_dir = Path(directory)
    fountain_files = sorted(reference_dir.glob("*.fountain"))
    failed = False

    for fountain_file in fountain_files:
        reference_docx = fountain_file.with_suffix(".docx")

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            actual_path = Path(f.name)
        try:
            screenplain.main.main([str(fountain_file), str(actual_path)])

            if not reference_docx.exists():
                shutil.copy2(actual_path, reference_docx)
                print(f"Generated reference: {reference_docx}")
                continue

            actual = _extract_structure(Document(str(actual_path)))
        finally:
            actual_path.unlink(missing_ok=True)

        expected = _extract_structure(Document(str(reference_docx)))
        if actual != expected:
            print(f"FAILED: {fountain_file.name}")
            failed = True
        else:
            print(f"OK: {fountain_file.name}")

    return not failed


if __name__ == "__main__":
    if not compare(FILES_DIR):
        sys.exit(1)
