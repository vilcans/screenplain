# Copyright (c) 2014 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from reportlab.lib import pagesizes
from reportlab.platypus import (
    BaseDocTemplate,
    Paragraph,
    Frame,
    PageTemplate,
)
from reportlab import platypus
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from screenplain.types import (
    Action, Dialog, DualDialog, Transition, Slug
)
from screenplain import types

lines_per_page = 55
characters_per_line = 61
frame_height = 12 * lines_per_page
frame_width = characters_per_line * 72 / 10.0  # Courier pitch is 10 chars/inch
page_width, page_height = pagesizes.letter
left_margin = 1.5 * inch
right_margin = page_width - left_margin - frame_width
top_margin = 1 * inch
bottom_margin = page_height - top_margin - frame_height

character_width = 1.0 / 10 * inch

default_style = ParagraphStyle(
    'default',
    fontName='Courier',
    fontSize=12,
    leading=12,
    spaceBefore=0,
    spaceAfter=0,
    leftIndent=0,
    rightIndent=0,
)
character_style = ParagraphStyle(
    'character', default_style,
    spaceBefore=12,
    leftIndent=19 * character_width,
    keepWithNext=1,
)
dialog_style = ParagraphStyle(
    'dialog', default_style,
    leftIndent=9 * character_width,
    rightIndent=frame_width - (45 * character_width),
)
parenthentical_style = ParagraphStyle(
    'parenthentical', default_style,
    leftIndent=13 * character_width,
    keepWithNext=1,
)
action_style = ParagraphStyle(
    'action', default_style,
    spaceBefore=12,
)
centered_action_style = ParagraphStyle(
    'centered-action', action_style,
    alignment=TA_CENTER,
)
slug_style = ParagraphStyle(
    'slug', default_style,
    spaceBefore=12,
    spaceAfter=12,
    keepWithNext=1,
)
transition_style = ParagraphStyle(
    'transition', default_style,
    spaceBefore=12,
    spaceAfter=12,
)


class DocTemplate(BaseDocTemplate):
    def __init__(self, *args, **kwargs):
        frame = Frame(
            left_margin, bottom_margin, frame_width, frame_height,
            id='normal',
            leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0
        )
        pageTemplates = [
            PageTemplate(id='standard', frames=[frame])
        ]
        BaseDocTemplate.__init__(
            self, pageTemplates=pageTemplates, *args, **kwargs
        )

    def handle_pageBegin(self):
        self.canv.setFont('Courier', 12, leading=12)
        page = self.page + 1
        if page >= 2:
            self.canv.drawRightString(
                left_margin + frame_width,
                page_height - 42,
                '%s.' % page
            )
        self._handle_pageBegin()


def add_paragraph(story, para, style):
    for line in para.lines:
        story.append(Paragraph(line.to_html(), style))


def add_dialog(story, dialog):
    story.append(Paragraph(dialog.character.to_html(), character_style))
    for parenthetical, line in dialog.blocks:
        if parenthetical:
            story.append(Paragraph(line.to_html(), parenthentical_style))
        else:
            story.append(Paragraph(line.to_html(), dialog_style))


def add_dual_dialog(story, dual):
    # TODO: format dual dialog
    add_dialog(story, dual.left)
    add_dialog(story, dual.right)


def to_pdf(screenplay, output_filename, template_constructor=DocTemplate):
    doc = template_constructor(
        output_filename,
        pagesize=(page_width, page_height),
    )
    story = []
    for para in screenplay:
        if isinstance(para, Dialog):
            add_dialog(story, para)
        elif isinstance(para, DualDialog):
            add_dual_dialog(story, para)
        elif isinstance(para, Action):
            add_paragraph(
                story, para,
                centered_action_style if para.centered else action_style
            )
        elif isinstance(para, Slug):
            add_paragraph(story, para, slug_style)
        elif isinstance(para, Transition):
            add_paragraph(story, para, transition_style)
        elif isinstance(para, types.PageBreak):
            story.append(platypus.PageBreak())
        else:
            # Ignore unknown types
            pass
    doc.build(story)
