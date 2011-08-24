import sys
import re
import cgi
from screenplain.parse import parse
import screenplain.parse

def unspace(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'>\s+<', '><', text)
    return text.strip()

head = unspace('''
<!doctype html>
<html>
  <head>
    <link rel="stylesheet" href="/style.css">
  </head>
  <body>
''')

paragraph_html = unspace("""
<div class="block">
    <p>%(margin)s</p>
    <div class="type type%(type)s">%(type)s</div>
    <p>%(text)s</p>
</div>
""")

foot = unspace('''
  </body>
</html>
''')

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
    out.write(head)
    for para in paragraphs:
        lines = para.format()
        margin = '<br>' * para.top_margin
        html_text = '<br>'.join(to_html(line) for line in lines)
        data = { 'type': types.get(type(para), '?'), 'text': html_text, 'margin': margin }
        out.write(paragraph_html % data)
    out.write(foot)
