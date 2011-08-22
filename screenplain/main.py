#!/usr/bin/env python

# Run with:
#   PYTHONPATH=. python screenplain/main.py filename.txt

import fileinput
import sys

if __name__ == '__main__':
    if True:
        from screenplain.export.text import to_text
        to_text(fileinput.input(), sys.stdout)
    else:
        from screenplain.export.pdf import to_pdf
        to_pdf(fileinput.input())
