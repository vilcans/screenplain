import sys
import codecs
from screenplain.parse import parse, get_pages

def to_text(screenplay, output_file):
    out = codecs.open(output_file, 'w', 'utf-8')
    for page_no, page in enumerate(get_pages(screenplay)):
        # page_no is 0-based
        if page_no != 0:
            out.write('\f')
        for line in page:
            out.write(line)
            out.write('\n')
