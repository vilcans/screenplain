# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from testcompat import TestCase
from StringIO import StringIO

from screenplain.export.pdf import to_pdf
from screenplain.richstring import plain, bold, italic


class OutputTests(TestCase):

    def setUp(self):
        self.out = StringIO()
        # TODO: figure out how to test PDF export

    def test_scene_heading_bold_underlined(self):
        self.assertEqual(1, 1)
        # TODO: test PDF exports Scene Headings as Bold and Underlined