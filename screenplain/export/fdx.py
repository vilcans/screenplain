from xml.sax.saxutils import escape

from screenplain.types import *
from screenplain.richstring import RichString, Bold, Italic, Underline

paragraph_types = {
    Slug: 'Scene Heading',
    Action: 'Action',
    Transition: 'Transition',
}

style_names = {
    Bold: 'Bold',
    Italic: 'Italic',
    Underline: 'Underline',
    RichString: None,
}


def _write_text_element(out, styles, text):
    style_value = '+'.join(str(s) for s in styles)
    if style_value == '':
        out.write('<Text>%s</Text>' % (escape(text)))
    else:
        out.write('<Text style="%s">%s</Text>' % (style_value, escape(text)))


def write_text(out, rich, parent_styles=None):
    parent_styles = parent_styles or set()
    style_name = style_names[type(rich)]
    if style_name:
        styles = parent_styles | set((style_name,))
    else:
        styles = parent_styles

    for segment in rich.segments:
        if isinstance(segment, basestring):
            _write_text_element(out, styles, segment)
        else:
            write_text(out, segment, styles)


def write_paragraph(out, para_type, lines):
    out.write('<Paragraph Type="%s">' % para_type)
    for line in lines:
        write_text(out, line)
    out.write('</Paragraph>')


def write_dialog(out, dialog):
    write_paragraph(out, 'Character', [dialog.character])
    for parenthetical, line in dialog.blocks:
        if parenthetical:
            write_paragraph(out, 'Parenthetical', [line])
        else:
            write_paragraph(out, 'Dialogue', [line])


def write_dual_dialog(out, dual):
    out.write('<Paragraph><DualDialogue>')
    write_dialog(out, dual.left)
    write_dialog(out, dual.right)
    out.write('</DualDialogue></Paragraph>')


def to_fdx(screenplay, out):

    out.write(
        '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>'
        '<FinalDraft DocumentType="Script" Template="No" Version="1">'
        '<Content>'
    )

    for para in screenplay:
        if isinstance(para, Dialog):
            write_dialog(out, para)
        elif isinstance(para, DualDialog):
            write_dual_dialog(out, para)
        else:
            para_type = paragraph_types[type(para)]
            write_paragraph(out, para_type, para.lines)
    out.write('</Content></FinalDraft>\n')
