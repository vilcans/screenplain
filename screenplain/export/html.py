# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from __future__ import with_statement
import sys
import re
import cgi
import os
import os.path

from screenplain.types import *


class tags(object):
    """Handler for automatically opening and closing tags.

    E.g.

    >>> import sys
    >>> from __future__ import with_statement
    >>> with tags(sys.stdout, 'div', 'p', 'a'):
    ...     sys.stdout.write('hello')
    ...
    <div><p><a>hello</a></p></div>

    Tags with attributes are also supported:

    >>> with tags(sys.stdout, 'div class="foo"'):
    ...     sys.stdout.write('hello')
    <div class="foo">hello</div>

    """
    def __init__(self, out, *tags):
        self.out = out
        self.tags = list(tags)

    def __enter__(self):
        for tag in self.tags:
            self.out.write('<%s>' % tag)

    def __exit__(self, exception_type, value, traceback):
        if not exception_type:
            for tag in reversed(self.tags):
                self.out.write('</%s>' % tag.split()[0])
        return False


def to_html(text):
    html = text.to_html()
    if html == '':
        return '&nbsp;'
    return re.sub('  ', '&nbsp; ', html)


def format_dialog(dialog, out):
    with tags(out, 'div class="dialog"'):
        _write_dialog_block(dialog, out)


def format_dual(dual, out):
    with tags(out, 'div class="dual"'):
        with tags(out, 'div class="left"'):
            _write_dialog_block(dual.left, out)
        with tags(out, 'div class="right"'):
            _write_dialog_block(dual.right, out)
        out.write('<br />')


def _write_dialog_block(dialog, out):
    with tags(out, 'p class="character"'):
        out.write(to_html(dialog.character))

    for parenthetical, text in dialog.blocks:
        if parenthetical:
            with tags(out, 'p class="parenthetical"'):
                out.write(to_html(text))
        else:
            with tags(out, 'p'):
                out.write(to_html(text))


def format_slug(slug, out):
    num = slug.scene_number
    with tags(out, 'h6'):
        if num:
            with tags(out, 'span class="scnuml"'):
                out.write(to_html(slug.scene_number))
        out.write(to_html(slug.line))
        if num:
            with tags(out, 'span class="scnumr"'):
                out.write(to_html(slug.scene_number))


def format_action(para, out):
    if para.centered:
        tag = 'div class="action centered"'
    else:
        tag = 'div class="action"'
    with tags(out, tag):
        for line in para.lines:
            with tags(out, 'p'):
                out.write(to_html(line))


def format_transition(para, out):
    with tags(out, 'div class="transition"'):
        out.write(to_html(para.line))


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
            format_slug(para, out)
        elif isinstance(para, Action):
            format_action(para, out)
        elif isinstance(para, Dialog):
            format_dialog(para, out)
        elif isinstance(para, DualDialog):
            format_dual(para, out)
        elif isinstance(para, Transition):
            format_transition(para, out)
        else:
            assert False, 'Unknown type: %s' % type(para)
        out.write('\n')
