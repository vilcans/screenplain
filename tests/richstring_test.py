# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from .testcompat import TestCase
from screenplain.richstring import (
    RichString, Segment,
    Bold, Italic,
    plain, bold, italic, underline,
    empty_string
)
from screenplain.richstring import parse_emphasis
from screenplain.types import Slug, Action, Dialog, DualDialog, Transition


class LowLevelRichStringTests(TestCase):

    def test_plain_string_has_one_single_segment(self):
        s = plain('hello')
        self.assertEqual(1, len(s.segments))
        self.assertEqual('hello', s.segments[0].text)
        self.assertEqual(set(), s.segments[0].styles)


class RichStringOperatorTests(TestCase):

    def test_repr(self):
        s = bold('Hello') + plain(' there ') + bold('folks')
        self.assertEqual(
            "(bold)('Hello') + (plain)(' there ') + (bold)('folks')",
            repr(s)
        )

    def test_repr_on_empty_string(self):
        self.assertEqual('empty_string', repr(empty_string))

    def test_unicode(self):
        s = bold('Hello') + plain(' there ') + bold('folks')
        self.assertEqual(
            u'Hello there folks',
            str(s)
        )

    def test_eq(self):
        self.assertEqual(bold('Hello'), bold('Hello'))
        self.assertNotEqual(bold('Hello'), bold('Foo'))
        self.assertNotEqual(plain('Hello'), bold('Hello'))

    def test_ne(self):
        self.assertFalse(bold('Hello') != bold('Hello'))

    def test_concatenating_two_richstrings(self):
        expected = RichString(Segment('hello', ()), Segment(' there', (Bold,)))
        s1 = plain('hello')
        s2 = bold(' there')
        result = s1 + s2
        self.assertEqual(expected, result)


class StyleGeneratorTests(TestCase):

    def test_bold_function_creates_bold_richstring(self):
        self.assertEqual(
            RichString(Segment('a', (Bold,))),
            bold('a')
        )

    def test_adding_functions(self):
        self.assertEqual(
            RichString(Segment('a', (Bold, Italic))),
            (bold + italic)('a')
        )


class RichStringTests(TestCase):

    def test_plain_to_html(self):
        self.assertEqual('hello', plain('hello').to_html())

    def test_to_html(self):
        s = (
            bold('bold') + plain(' normal ') +
            italic('italic') + underline('wonderline')
        )
        self.assertEqual(
            '<strong>bold</strong> normal <em>italic</em><u>wonderline</u>',
            s.to_html()
        )


class ParseEmphasisTests(TestCase):

    def test_parse_without_emphasis(self):
        self.assertEqual(
            plain('Hello'), parse_emphasis('Hello'),
            'Expected parse_emphasis to return a plain string')

    def test_parse_bold(self):
        self.assertEqual(
            parse_emphasis('**Hello**'),
            bold('Hello')
        )

    def test_parse_pre_and_postfix_and_bold(self):
        self.assertEqual(
            parse_emphasis('pre**Hello**post'),
            plain('pre') + bold('Hello') + plain('post')
        )

    def test_parse_multiple_bold(self):
        self.assertEqual(
            parse_emphasis('x**Hello** **there**'),
            plain('x') + bold('Hello') + plain(' ') + bold('there')
        )

    def test_parse_adjacent_bold(self):
        self.assertEqual(
            parse_emphasis('**123**456**'),
            bold('123') + plain('456**')
        )

    def test_italic(self):
        self.assertEqual(
            parse_emphasis('*Italian style*'),
            italic('Italian style')
        )

    def test_bold_inside_italic(self):
        self.assertEqual(
            parse_emphasis('*Swedish **style** rules*'),
            italic('Swedish ') + (bold + italic)('style') + italic(' rules')
        )

    def test_italic_inside_bold(self):
        self.assertEqual(
            parse_emphasis('**Swedish *style* rules**'),
            bold('Swedish ') + (bold + italic)('style') + bold(' rules')
        )

    def test_italic_and_bold(self):
        self.assertEqual(
            parse_emphasis('***really strong***'),
            (bold + italic)('really strong')
        )

    def test_additional_star(self):
        self.assertEqual(
            parse_emphasis('*foo* bar* baz'),
            italic('foo') + plain(' bar* baz')
        )

    def test_underline(self):
        self.assertEqual(
            parse_emphasis('_hello_'),
            underline('hello')
        )

    def test_bold_inside_underline(self):
        self.assertEqual(
            parse_emphasis('_**hello**_'),
            (bold + underline)('hello')
        )

    def test_overlapping_underscore_and_italic(self):
        # It's unclear what result to expect in this case.
        # This is one way of interpreting it
        self.assertEqual(
            parse_emphasis('_*he_llo*'),
            (italic + underline)('he') + italic('llo')
        )

    def test_complicated(self):
        # As reported by Stu
        self.assertEqual(
            parse_emphasis(
                'You can _underline_ words, make them **bold** or *italic* '
                'or even ***bold italic.***'
            ), (
                plain('You can ') + underline('underline') +
                plain(' words, make them ') + bold('bold') + plain(' or ') +
                italic('italic') + plain(' or even ') +
                (bold + italic)('bold italic.')
            )
        )

    def test_simplified_complicated(self):
        self.assertEqual(
            parse_emphasis('*italic* or even ***bold italic.***'),
            italic('italic') + plain(' or even ') +
            (bold + italic)('bold italic.')
        )

    def test_two_italic_should_not_create_one_long_italic_string(self):
        self.assertEqual(
            parse_emphasis('*first* *second*'),
            italic('first') + plain(' ') + italic('second')
        )

    def test_two_bold_should_not_create_one_long_bold_string(self):
        self.assertEqual(
            parse_emphasis('**first** **second**'),
            bold('first') + plain(' ') + bold('second')
        )

    def test_escaping_star_creates_a_literal_star(self):
        self.assertEqual(
            parse_emphasis(r'\*hello*'),
            plain('*hello*')
        )
