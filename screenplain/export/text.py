import sys
from screenplain.parse import parse, get_pages

def to_text(input, out):
    paragraphs = parse(input)
    for page_no, page in enumerate(get_pages(paragraphs)):
        # page_no is 0-based
        if page_no != 0:
            out.write('\f')
        for line in page:
            out.write(line)
            out.write('\n')
