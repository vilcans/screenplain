from __future__ import with_statement
import sys
import re
import cgi
import os
import os.path

from screenplain.types import *


types = {
    Slug: 'slug',
    Dialog: 'dialog',
    DualDialog: 'dual',
    Action: 'action',
    Transition: 'transition',
}


def to_html(text):
    return re.sub('  ', '&nbsp; ', text.to_html())


def format_dialog(dialog, out):
    out.write(
        '<p class="character">'
    )
    out.write(to_html(dialog.character))
    out.write('</p>')

    for parenthetical, text in dialog.blocks:
        if parenthetical:
            out.write('<p class="parenthetical">')
            out.write(to_html(text))
            out.write('</p>')
        else:
            out.write('<p>')
            out.write(to_html(text))
            out.write('</p>')


def format_dual(dual, out):
    out.write(
        '<div class="left dialog">'
    )
    format_dialog(dual.left, out)
    out.write(
        '</div>'
        '<div class="right dialog">'
    )
    format_dialog(dual.right, out)
    out.write(
        '</div>'
        '<br />'
    )


def format_slug(slug, out):
    out.write('<h2>')
    out.write(to_html(slug.line))
    out.write('</h2>')


def _read_file(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as stream:
        return stream.read()


def convert(screenplay, out, annotated=False):

    css = _read_file('default.css')
    out.write(
        '<!DOCTYPE html>\n'
        '<html>'
        '<head>'
        '<title>Screenplay</title>'
        '<style type="text/css">'
    )
    out.write(css)
    out.write(
        '</style>'
        '</head>'
        '<body>'
        '<div class="screenplay">\n'
    )
    convert_body_html(screenplay, out)
    out.write(
        '</div>'
        '</body>'
        '</html>\n'
    )


def convert_body_html(screenplay, out):
    for para in screenplay:
        if isinstance(para, Slug):
            # Slugs are h2 tags not inside a div
            format_slug(para, out)
        elif isinstance(para, Dialog):
            out.write('<div class="dialog">')
            format_dialog(para, out)
            out.write('</div>')
        elif isinstance(para, DualDialog):
            out.write('<div class="dual">')
            format_dual(para, out)
            out.write('</div>')
        else:
            classname = types.get(type(para))
            out.write('<div class="')
            out.write(classname)
            out.write('">')
            for line in para.lines:
                out.write('<p>')
                out.write(to_html(line))
                out.write('</p>')
            out.write('</div>')
        out.write('\n')
