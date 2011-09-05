import sys
import re
import cgi
from screenplain.parse import parse
import screenplain.parse

def unspace(text):
    text = re.sub(r'\s+', ' ', text)
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
    screenplain.parse.Slug: 'Slug',
    screenplain.parse.Dialog: 'Dialog',
    screenplain.parse.DualDialog: 'Dual',
    screenplain.parse.Action: 'Action',
    screenplain.parse.Transition: 'Transition',
}

def to_html(text):
    return re.sub('  ', '&nbsp; ', cgi.escape(text))

def to_annotated_html(input, out):
    paragraphs = parse(input)
    for para in paragraphs:
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

