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
    <div class="type %(type)s">%(type)s</div>
    %(text)s
</div>
""")

types = {
    Slug: 'slug',
    Dialog: 'dialog',
    DualDialog: 'dual',
    Action: 'action',
    Transition: 'transition',
}


def to_html(text):
    return re.sub('  ', '&nbsp; ', text.to_html())


def format_dialog(dialog):
    yield '<p class="character">%s</p>' % to_html(dialog.character)

    for parenthetical, text in dialog.blocks:
        yield '<p class="%s">%s</p>' % (
            'parenthetical' if parenthetical else 'dialog',
            to_html(text)
        )


def format_dual(dual):
    yield (
        '<div class="dual-dialog">'
        '<div class="dual left">'
    )
    for html in format_dialog(dual.left):
        yield html
    yield (
        '</div>'
        '<div class="dual right">'
    )
    for html in format_dialog(dual.right):
        yield html
    yield (
        '</div>'
        '<br/>'
        '</div>'
    )


def to_annotated_html(screenplay, out):
    for para in screenplay:
        classname = types.get(type(para))
        if isinstance(para, Dialog):
            html_text = ''.join(format_dialog(para))
        elif isinstance(para, DualDialog):
            html_text = ''.join(format_dual(para))
        else:
            lines = para.lines
            html_text = ''.join(
                '<p class="%s">%s</p>' % (classname, to_html(line))
                for line in para.lines
            )

        margin = '<p>&nbsp;</p>' * para.top_margin
        data = {
            'type': classname,
            'text': html_text,
            'margin': margin
        }
        out.write(paragraph_html % data)
