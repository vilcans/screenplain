import unittest2
from StringIO import StringIO

from screenplain.export.fdx import write_text

from screenplain.richstring import RichString, Bold, Italic


class OutputTests(unittest2.TestCase):

    def setUp(self):
        self.out = StringIO()

    def test_plain_text_should_have_no_style(self):
        write_text(self.out, RichString('hello'))
        self.assertEqual(
            self.out.getvalue(),
            '<Text>hello</Text>'
        )

    def test_bold_text_should_have_bold_style(self):
        write_text(self.out, Bold('hello'))
        self.assertEqual(
            self.out.getvalue(),
            '<Text style="Bold">hello</Text>'
        )

    def test_sequential_styles(self):
        rich = RichString('plain', Bold('b'), Italic('i'))
        write_text(self.out, rich)
        self.assertEqual(
            self.out.getvalue(),
            '<Text>plain</Text>'
            '<Text style="Bold">b</Text>'
            '<Text style="Italic">i</Text>'
        )

    def test_nested_styles(self):
        rich = Bold('outer', Italic('inner'), 'outer')
        write_text(self.out, rich)
        self.assertEqual(
            self.out.getvalue(),
            '<Text style="Bold">outer</Text>'
            '<Text style="Bold+Italic">inner</Text>'
            '<Text style="Bold">outer</Text>'
        )
