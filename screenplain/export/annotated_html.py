import sys
import re
import cgi
from screenplain.types import *

def unspace(text):
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r'\s\s+', ' ', text)
    text = re.sub(r'>\s+<', '><', text)
    return text.strip()

paragraph_html = unspace("""
<div class="block">
    %(margin)s
    <div class="type type%(type)s">%(type)s</div>
    %(text)s
</div>
""")

types = {
    Slug: 'Slug',
    Dialog: 'Dialog',
    DualDialog: 'Dual',
    Action: 'Action',
    Transition: 'Transition',
}

def to_html(text):
    return re.sub('  ', '&nbsp; ', cgi.escape(text))

def to_annotated_html(screenplay, out):
    for para in screenplay:
        lines = para.format()
        margin = '<p>&nbsp;</p>' * para.top_margin
        html_text = ''.join(
            '<p>%s</p>' % to_html(line) for line in lines
        )
        data = {
            'type': types.get(type(para), '?'),
            'text': html_text,
            'margin': margin
        }
        out.write(paragraph_html % data)

