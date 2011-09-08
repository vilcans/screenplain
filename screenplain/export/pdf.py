#!/usr/bin/python
import fileinput
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes

from screenplain.format import get_pages

def to_pdf(screenplay, output_file):
    # pagesizes.letter, pagesizes.A4
    page_width, page_height = pagesizes.A4
    c = canvas.Canvas(output_file, pagesize=pagesizes.A4)
    c.setFont('Courier', 12)

    for page_no, page in enumerate(get_pages(screenplay), 1):
        if page_no != 1:
            c.showPage()
        c.setFont('Courier', 12)
        for line_no, line in enumerate(page):
            c.drawString(0, page_height - 12 - 12 * line_no, line)
    c.save()

if __name__ == '__main__':
    to_pdf(fileinput.input())
