#!/usr/bin/env python3

"""Regression test for PDF generation.

Runs screenplain on each .fountain file in the given directory,
generating a PDF file and comparing it to the corresponding reference
PDF file using diff-pdf.

diff-pdf can be installed on Debian with:

    sudo apt install diff-pdf-wx
"""

import subprocess
from pathlib import Path
import sys
import screenplain.main


def compare(directory) -> bool:
    """Test that PDF generation produces consistent output."""
    reference_dir = Path(directory)
    fountain_files = list(reference_dir.glob("*.fountain"))
    failed = False

    for fountain_file in fountain_files:
        reference_pdf = fountain_file.with_suffix(".pdf")
        if not reference_pdf.exists():
            continue  # Skip if no reference PDF exists

        print(f"Comparing {reference_pdf}...")
        actual_file = fountain_file.with_stem(
            fountain_file.stem + "-actual"
        ).with_suffix(".pdf")
        diff_path = actual_file.with_stem(
            fountain_file.stem + "-diff"
        ).with_suffix(".pdf")

        # Generate PDF using screenplain Python API
        screenplain.main.main([str(fountain_file), str(actual_file)])

        # Compare files using diff-pdf (visual comparison)
        result = subprocess.run(
            [
                "diff-pdf",
                "--skip-identical",
                "--output-diff",
                diff_path,
                str(reference_pdf),
                actual_file,
            ],
            capture_output=True,
        )
        if result.returncode != 0:
            print(
                f"FAILED: Generated PDF differs visually from reference: "
                f"{fountain_file}"
            )
            print(f"reference: {reference_pdf}")
            print(f"actual: {actual_file}")
            print(f"diff: {diff_path}")
            failed = True
        else:
            # Remove comparison files if not difference found
            Path(actual_file).unlink()
            Path(diff_path).unlink()

    return not failed


if __name__ == "__main__":
    for path in ["tests/files", "examples"]:
        if not compare(path):
            sys.exit(1)
