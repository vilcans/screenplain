# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from io import BytesIO
from unittest import TestCase

from screenplain.export.docx import to_docx
from screenplain.richstring import bold, italic, plain, underline
from screenplain.types import (
    Action,
    Dialog,
    DualDialog,
    PageBreak,
    Screenplay,
    Section,
    Slug,
    Transition,
)
from tests.docx_reader import Document


def _convert(paragraphs):
    screenplay = Screenplay(paragraphs=paragraphs)
    buf = BytesIO()
    to_docx(screenplay, buf)
    buf.seek(0)
    return Document(buf)


class SlugTests(TestCase):
    def test_slug_uses_scene_heading_style(self):
        doc = _convert([Slug(plain("INT. ROOM - DAY"))])
        self.assertEqual(doc.paragraphs[0].style_name, "SP Scene Heading")

    def test_slug_text(self):
        doc = _convert([Slug(plain("INT. ROOM - DAY"))])
        self.assertEqual(doc.paragraphs[0].text, "INT. ROOM - DAY")

    def test_slug_plain_run_inherits_bold_from_style(self):
        doc = _convert([Slug(plain("INT. ROOM - DAY"))])
        self.assertIsNone(doc.paragraphs[0].runs[0].bold)


class ActionTests(TestCase):
    def test_action_uses_action_style(self):
        doc = _convert([Action([plain("Some action.")])])
        self.assertEqual(doc.paragraphs[0].style_name, "SP Action")

    def test_action_text(self):
        doc = _convert([Action([plain("Some action.")])])
        self.assertEqual(doc.paragraphs[0].text, "Some action.")

    def test_multiline_action_produces_multiple_paragraphs(self):
        doc = _convert([Action([plain("Line one."), plain("Line two.")])])
        self.assertEqual(len(doc.paragraphs), 2)
        self.assertEqual(doc.paragraphs[0].text, "Line one.")
        self.assertEqual(doc.paragraphs[1].text, "Line two.")

    def test_centered_action_has_center_alignment(self):
        doc = _convert([Action([plain("Centered.")], centered=True)])
        self.assertEqual(doc.paragraphs[0].alignment, "center")


class TransitionTests(TestCase):
    def test_transition_uses_transition_style(self):
        doc = _convert([Transition(plain("CUT TO:"))])
        self.assertEqual(doc.paragraphs[0].style_name, "SP Transition")

    def test_transition_text(self):
        doc = _convert([Transition(plain("CUT TO:"))])
        self.assertEqual(doc.paragraphs[0].text, "CUT TO:")


class DialogTests(TestCase):
    def _make_dialog(self):
        d = Dialog(plain("ALICE"))
        d.add_line(plain("Hello there."))
        return d

    def test_character_style(self):
        doc = _convert([self._make_dialog()])
        self.assertEqual(doc.paragraphs[0].style_name, "SP Character")
        self.assertEqual(doc.paragraphs[0].text, "ALICE")

    def test_dialogue_style(self):
        doc = _convert([self._make_dialog()])
        self.assertEqual(doc.paragraphs[1].style_name, "SP Dialogue")
        self.assertEqual(doc.paragraphs[1].text, "Hello there.")

    def test_parenthetical_style(self):
        d = Dialog(plain("ALICE"))
        d.add_line(plain("(quietly)"))
        d.add_line(plain("Hello there."))
        doc = _convert([d])
        self.assertEqual(doc.paragraphs[1].style_name, "SP Parenthetical")
        self.assertEqual(doc.paragraphs[1].text, "(quietly)")
        self.assertEqual(doc.paragraphs[2].style_name, "SP Dialogue")


class DualDialogTests(TestCase):
    def _make_dual(self):
        left = Dialog(plain("ALICE"))
        left.add_line(plain("Hello."))
        right = Dialog(plain("BOB"))
        right.add_line(plain("Hi."))
        return DualDialog(left, right)

    def test_dual_dialog_creates_table(self):
        doc = _convert([self._make_dual()])
        self.assertEqual(len(doc.tables), 1)
        self.assertEqual(len(doc.tables[0].columns), 2)

    def test_dual_dialog_left_cell_content(self):
        doc = _convert([self._make_dual()])
        left_cell = doc.tables[0].rows[0].cells[0]
        texts = [p.text for p in left_cell.paragraphs]
        self.assertIn("ALICE", texts)
        self.assertIn("Hello.", texts)

    def test_dual_dialog_right_cell_content(self):
        doc = _convert([self._make_dual()])
        right_cell = doc.tables[0].rows[0].cells[1]
        texts = [p.text for p in right_cell.paragraphs]
        self.assertIn("BOB", texts)
        self.assertIn("Hi.", texts)


class RichTextTests(TestCase):
    def test_bold_run(self):
        doc = _convert([Action([bold("Important")])])
        self.assertTrue(doc.paragraphs[0].runs[0].bold)

    def test_italic_run(self):
        doc = _convert([Action([italic("emphasis")])])
        self.assertTrue(doc.paragraphs[0].runs[0].italic)

    def test_underline_run(self):
        doc = _convert([Action([underline("underlined")])])
        self.assertTrue(doc.paragraphs[0].runs[0].underline)

    def test_mixed_styles_produce_multiple_runs(self):
        doc = _convert([Action([plain("normal") + bold("bold")])])
        runs = doc.paragraphs[0].runs
        self.assertEqual(len(runs), 2)
        self.assertIsNone(runs[0].bold)
        self.assertTrue(runs[1].bold)


class SectionTests(TestCase):
    def test_section_uses_heading_style(self):
        doc = _convert([Section(plain("ACT ONE"), level=1)])
        self.assertEqual(doc.paragraphs[0].style_name, "Heading 1")
        self.assertEqual(doc.paragraphs[0].text, "ACT ONE")

    def test_section_level_maps_to_heading_number(self):
        doc = _convert([Section(plain("Scene"), level=2)])
        self.assertEqual(doc.paragraphs[0].style_name, "Heading 2")

    def test_section_synopsis(self):
        s = Section(plain("ACT ONE"), level=1)
        s.set_synopsis("The beginning.")
        doc = _convert([s])
        self.assertEqual(doc.paragraphs[1].style_name, "SP Synopsis")
        self.assertEqual(doc.paragraphs[1].text, "The beginning.")

    def test_slug_synopsis(self):
        slug = Slug(plain("INT. ROOM - DAY"))
        slug.set_synopsis("A quiet room.")
        doc = _convert([slug])
        self.assertEqual(doc.paragraphs[1].style_name, "SP Synopsis")
        self.assertEqual(doc.paragraphs[1].text, "A quiet room.")


class TitlePageTests(TestCase):
    def test_title_page_centered_fields(self):
        screenplay = Screenplay(
            title_page={"Title": ["My Film"], "Author": ["Jane Smith"]},
        )
        buf = BytesIO()
        to_docx(screenplay, buf)
        buf.seek(0)
        doc = Document(buf)
        texts = [p.text for p in doc.paragraphs]
        self.assertIn("My Film", texts)
        self.assertIn("Jane Smith", texts)

    def test_title_page_followed_by_page_break(self):
        screenplay = Screenplay(
            title_page={"Title": ["My Film"]},
            paragraphs=[Action([plain("INT. ROOM - DAY")])],
        )
        buf = BytesIO()
        to_docx(screenplay, buf)
        buf.seek(0)
        doc = Document(buf)
        xmls = [p.xml for p in doc.paragraphs]
        self.assertTrue(any('w:type="page"' in x for x in xmls))


class PageBreakTests(TestCase):
    def test_page_break_is_inserted(self):
        doc = _convert(
            [
                Action([plain("Before.")]),
                PageBreak(),
                Action([plain("After.")]),
            ]
        )
        self.assertEqual(len(doc.paragraphs), 3)
        xml = doc.paragraphs[1].xml
        self.assertIn('w:type="page"', xml)
