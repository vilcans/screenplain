import sys
import codecs
from screenplain.format import get_pages


def to_text(screenplay, out):
    for page_no, page in enumerate(get_pages(screenplay)):
        # page_no is 0-based
        if page_no != 0:
            out.write('\f')
        for line in page:
            out.write(line)
            out.write('\n')
