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
from screenplain.richstring import plain


class tag(object):
    """Handler for automatically opening and closing a tag.

    E.g.

    >>> import sys
    >>> from __future__ import with_statement
    >>> with tag(sys.stdout, 'div'):
    ...     sys.stdout.write('hello')
    ...
    <div>hello</div>

    Adding classes to the element is possible:

    >>> with tag(sys.stdout, 'div', classes='action'):
    ...     sys.stdout.write('hello')
    <div class="action">hello</div>

    >>> with tag(sys.stdout, 'div', classes=['action', 'centered']):
    ...     sys.stdout.write('hello')
    <div class="action centered">hello</div>

    """
    def __init__(self, out, tag, classes=None):
        self.out = out
        self.tag = tag
        if isinstance(classes, basestring):
            self.classes = [classes]
        else:
            self.classes = classes

    def __enter__(self):
        if self.classes:
            self.out.write('<%s class="%s">' % (
                self.tag,
                ' '.join(self.classes)
            ))
        else:
            self.out.write('<%s>' % self.tag)

    def __exit__(self, exception_type, value, traceback):
        if not exception_type:
            self.out.write('</%s>' % self.tag)
        return False


def to_html(text):
    html = text.to_html()
    if html == '':
        return '&nbsp;'
    return re.sub('  ', '&nbsp; ', html)


def format_dialog(dialog, out):
    with tag(out, 'div', classes='dialog'):
        _write_dialog_block(dialog, out)


def format_dual(dual, out):
    with tag(out, 'div', classes='dual'):
        with tag(out, 'div', classes='left'):
            _write_dialog_block(dual.left, out)
        with tag(out, 'div', classes='right'):
            _write_dialog_block(dual.right, out)
        out.write('<br />')


def _write_dialog_block(dialog, out):
    with tag(out, 'p', classes='character'):
        out.write(to_html(dialog.character))

    for parenthetical, text in dialog.blocks:
        classes = 'parenthetical' if parenthetical else None
        with tag(out, 'p', classes=classes):
            out.write(to_html(text))


def format_slug(slug, out):
    num = slug.scene_number
    with tag(out, 'h6'):
        if num:
            with tag(out, 'span', classes='scnuml'):
                out.write(to_html(slug.scene_number))
        out.write(to_html(slug.line))
        if num:
            with tag(out, 'span', classes='scnumr'):
                out.write(to_html(slug.scene_number))
    if slug.synopsis:
        with tag(out, 'span', classes='h6-synopsis'):
            out.write(to_html(plain(slug.synopsis)))


def format_section(section, out):
    with tag(out, 'h%d' % section.level):
        out.write(to_html(section.text))
    if section.synopsis:
        with tag(out, 'span', classes='h%d-synopsis' % section.level):
            out.write(to_html(plain(section.synopsis)))


def format_action(para, out):
    classes = ['action']
    if para.centered:
        classes.append('centered')
    with tag(out, 'div', classes=classes):
        with tag(out, 'p'):
            for number, line in enumerate(para.lines):
                if number != 0:
                    out.write('<br/>')
                out.write(to_html(line))


def format_transition(para, out):
    with tag(out, 'div', classes='transition'):
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
        '<div id="wrapper" class="screenplay">\n'
    )
    convert_bare(screenplay, out)
    out.write(
        '</div>'
        '</body>'
        '</html>\n'
    )

_format_functions = {
    Slug: format_slug,
    Action: format_action,
    Dialog: format_dialog,
    DualDialog: format_dual,
    Transition: format_transition,
    Section: format_section,
}


def convert_bare(screenplay, out):
    """Convert the screenplay into HTML, written to the file-like object `out`.
    Does not create a complete HTML document, as it doesn't include
    <html>, <body>, etc.

    """
    for para in screenplay:
        format_function = _format_functions.get(type(para), None)
        if format_function:
            format_function(para, out)
            out.write('\n')
