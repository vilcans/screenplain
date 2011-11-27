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
        '<div class="left">'
    )
    format_dialog(dual.left, out)
    out.write(
        '</div>'
        '<div class="right">'
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


def format_action(para, out):
    if para.centered:
        out.write('<div class="action centered">')
    else:
        out.write('<div class="action">')
    for line in para.lines:
        out.write('<p>')
        out.write(to_html(line))
        out.write('</p>')
    out.write('</div>')


def format_transition(para, out):
    out.write('<div class="transition">')
    out.write(to_html(para.line))
    out.write('</div>')


def _read_file(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as stream:
        return stream.read()


def convert(screenplay, out, bare=False):
    """Convert the screenplay into HTML, written to the file-like object `out`.

    The output will be a complete HTML document unless `bare` is true.

    """
    if bare:
        convert_bare(screenplay, out)
    else:
        convert_full(screenplay, out)


def convert_full(screenplay, out):
    """Convert the screenplay into a complete HTML document,
    written to the file-like object `out`.

    """
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
    convert_bare(screenplay, out)
    out.write(
        '</div>'
        '</body>'
        '</html>\n'
    )


def convert_bare(screenplay, out):
    """Convert the screenplay into HTML, written to the file-like object `out`.
    Does not create a complete HTML document, as it doesn't include
    <html>, <body>, etc.

    """
    for para in screenplay:
        if isinstance(para, Slug):
            # Slugs are h2 tags not inside a div
            format_slug(para, out)
        elif isinstance(para, Action):
            format_action(para, out)
        elif isinstance(para, Dialog):
            out.write('<div class="dialog">')
            format_dialog(para, out)
            out.write('</div>')
        elif isinstance(para, DualDialog):
            out.write('<div class="dual">')
            format_dual(para, out)
            out.write('</div>')
        elif isinstance(para, Transition):
            format_transition(para, out)
        else:
            assert False, 'Unknown type: %s' % type(para)
        out.write('\n')
