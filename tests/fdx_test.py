# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from testcompat import TestCase
from six import StringIO

from screenplain.export.fdx import write_text
from screenplain.richstring import plain, bold, italic


class OutputTests(TestCase):

    def setUp(self):
        self.out = StringIO()

    def test_plain_text_should_have_no_style(self):
        write_text(self.out, plain('hello'), False)
        self.assertEqual(
            self.out.getvalue(),
            '      <Text>hello</Text>\n'
        )

    def test_bold_text_should_have_bold_style(self):
        write_text(self.out, bold('hello'), False)
        self.assertEqual(
            self.out.getvalue(),
            '      <Text Style="Bold">hello</Text>\n'
        )

    def test_sequential_styles(self):
        rich = plain('plain') + bold('b') + italic('i')
        write_text(self.out, rich, False)
        self.assertEqual(
            self.out.getvalue(),
            '      <Text>plain</Text>\n'
            '      <Text Style="Bold">b</Text>\n'
            '      <Text Style="Italic">i</Text>\n'
        )

    def test_several_styles(self):
        rich = bold('outer') + (bold + italic)('inner') + bold('outer')
        write_text(self.out, rich, False)
        self.assertEqual(
            self.out.getvalue(),
            '      <Text Style="Bold">outer</Text>\n'
            '      <Text Style="Bold+Italic">inner</Text>\n'
            '      <Text Style="Bold">outer</Text>\n'
        )

    def test_write_text_adds_line_break_if_requested(self):
        rich = bold('outer') + (bold + italic)('inner') + bold('outer')
        write_text(self.out, rich, True)
        self.assertEqual(
            self.out.getvalue(),
            '      <Text Style="Bold">outer</Text>\n'
            '      <Text Style="Bold+Italic">inner</Text>\n'
            '      <Text Style="Bold">outer\n</Text>\n'  # note newline
        )
