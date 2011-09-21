import unittest2
from screenplain.richstring import RichString, Bold, Italic, Underline
from screenplain.richstring import parse_emphasis
from screenplain.types import Slug, Action, Dialog, DualDialog, Transition


class RichStringOperatorTests(unittest2.TestCase):

    def test_repr(self):
        s = RichString(Bold('Hello'), ' there ', Bold('folks'))
        self.assertEquals(
            "RichString(Bold('Hello'), ' there ', Bold('folks'))",
            repr(s)
        )

    def test_eq(self):
        self.assertEquals(Bold('Hello'), Bold('Hello'))
        self.assertNotEquals(Bold('Hello'), Bold('Foo'))
        self.assertNotEquals('Hello', Bold('Hello'))
        self.assertEquals(
            Bold('a', Italic('b'), 'c'),
            Bold('a', Italic('b'), 'c')
        )
        self.assertNotEquals(
            Bold('a', Italic('b'), 'c'),
            Bold('a', Italic('b'), 'd')
        )

    def test_ne(self):
        self.assertFalse(Bold('Hello') != Bold('Hello'))


class RichStringTests(unittest2.TestCase):

    def test_to_html(self):
        s = RichString(
            Bold('bold'),
            ' normal ',
            Italic('italic'),
            Underline('wonderline')
        )
        self.assertEquals(
            '<strong>bold</strong> normal <em>italic</em><u>wonderline</u>',
            s.to_html()
        )


class ParseEmphasisTests(unittest2.TestCase):

    def test_parse_without_emphasis(self):
        self.assertEquals(RichString('Hello'), parse_emphasis('Hello'),
            'Expected parse_emphasis to return a string')

    def test_parse_bold(self):
        self.assertEquals(
            parse_emphasis('**Hello**'),
            Bold('Hello')
        )

    def test_parse_pre_and_postfix_and_bold(self):
        self.assertEquals(
            parse_emphasis('pre**Hello**post'),
            RichString('pre', Bold('Hello'), 'post'),
        )

    def test_parse_multiple_bold(self):
        self.assertEquals(
            parse_emphasis('x**Hello** **there**'),
            RichString('x', Bold('Hello'), ' ', Bold('there'))
        )

    def test_parse_adjacent_bold(self):
        self.assertEquals(
            parse_emphasis('**123****456**'),
            RichString(Bold('123**'), '456**')
        )

    def test_italic(self):
        self.assertEquals(
            parse_emphasis('*Italian style*'),
            Italic('Italian style')
        )

    def test_bold_inside_italic(self):
        self.assertEquals(
            parse_emphasis('*Swedish **style** rules*'),
            Italic('Swedish ', Bold('style'), ' rules')
        )

    def test_italic_inside_bold(self):
        self.assertEquals(
            parse_emphasis('**Swedish *style* rules**'),
            Bold('Swedish ', Italic('style'), ' rules')
        )

    def test_italic_and_bold(self):
        self.assertEquals(
            parse_emphasis('***really strong***'),
            Bold(Italic('really strong'))
        )

    @unittest2.expectedFailure
    def test_additional_star(self):
        self.assertEquals(
            parse_emphasis('*foo* bar* baz'),
            RichString(Italic('foo'), ' bar* baz')
        )

    def test_underline(self):
        self.assertEquals(
            parse_emphasis('_hello_'),
            Underline('hello')
        )

    def test_bold_inside_underline(self):
        self.assertEquals(
            parse_emphasis('_**hello**_'),
            Underline(Bold('hello'))
        )

    def test_overlapping_underscore_and_italic(self):
        self.assertEquals(
            parse_emphasis('_*he_llo*'),
            RichString(Underline('*he'), 'llo*')
        )
