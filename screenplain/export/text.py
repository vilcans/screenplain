import sys
from screenplain.parse import parse, get_pages

def to_text(input):
    out = sys.stdout
    paragraphs = parse(input)
    for page_no, page in enumerate(get_pages(paragraphs), 1):
        if page_no != 1:
            out.write('\f')
        for line in page:
            out.write(line)
            out.write('\n')
