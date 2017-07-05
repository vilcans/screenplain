from PDF import PdfFileReader
from io import BytesIO

from screenplain.export import html
from screenplain.export.html import dialog_numbers_css
from screenplain.export import pdf
from screenplain.parsers import fountain

from testcompat import TestCase


script = """

EXT. DESSERT ISLAND - DAY

ROBERT
I've told you a thousand times, I do not care for sea urchins.

WALTER
Given our current situation, I hardly think we can afford to picky!

ROBERT
Listen Walt, I'm a kelp man - through and through!
(staring determinedly into the mid-foredistance)
My father was a kelp man...

ROBERT
...and his father before him.

WALTER ^
(sarcastically)
"...and his father before him." ...

WALTER
I've heard it all before.
(pause)
Hey.  This island is made of pie.

"""


class DialogNumberingTests(TestCase):

    def setUp(self):
        self.screenplay = fountain.parse(BytesIO(script))

    def _extract_character_lines_from_pdf(self, pdf_file):
        pdf_reader = PdfFileReader(pdf_file)
        page_1 = pdf_reader.getPage(0)
        text = page_1.extractText()
        lines = text.split('\n')
        character_lines = [line for line in lines
                           if line.startswith('WALTER') or
                           line.startswith('ROBERT')]
        return character_lines

    def test_pdf_without_numbering(self):
        pdf_file = BytesIO()
        pdf.to_pdf(self.screenplay, output_filename=pdf_file, numbered=False)
        character_lines = self._extract_character_lines_from_pdf(pdf_file)
        assert character_lines == ['ROBERT',
                                   'WALTER',
                                   'ROBERT',
                                   'ROBERT',
                                   'WALTER',
                                   'WALTER',
                                   ]

    def test_pdf_with_numbering(self):
        pdf_file = BytesIO()
        pdf.to_pdf(self.screenplay, output_filename=pdf_file, numbered=True)
        character_lines = self._extract_character_lines_from_pdf(pdf_file)
        assert character_lines == ['ROBERT 1',
                                   'WALTER 2',
                                   'ROBERT 3',
                                   'ROBERT 4',
                                   'WALTER 5',
                                   'WALTER 6',
                                   ]

    def _test_html(self, bare, numbered, expected):
        html_file = BytesIO()
        html.convert(self.screenplay, out=html_file, bare=bare,
                     numbered=numbered)
        generated_html = html_file.getvalue()
        return (dialog_numbers_css in generated_html) is expected

    def test_html_numbering(self):
        assert self._test_html(bare=False, numbered=False, expected=False)
        assert self._test_html(bare=False, numbered=True, expected=True)
        assert self._test_html(bare=True, numbered=False, expected=False)
        assert self._test_html(bare=True, numbered=True, expected=False)
