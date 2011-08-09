import itertools
import textwrap

# Numbers from http://www.emacswiki.org/emacs/ScreenPlay
# According to http://johnaugust.com/2004/how-many-lines-per-page
lines_per_page = 56

class _ParentheticalFlipFlop(object):
    def __init__(self):
        self.inside = False

    def __call__(self, text):
        stripped = text.strip()
        starts = stripped.startswith('(')
        ends = stripped.endswith(')')

        if self.inside:
            if ends:
                self.inside = False
            return True
        else:
            if starts and not ends:
                self.inside = True
            return starts

class Slug(object):
    indent = ''
    top_margin = 1

    def __init__(self, lines):
        self.lines = [self.indent + line.strip() for line in lines]

    def format(self):
        return self.lines

class Dialog(object):
    indent_character = ' ' * 22
    indent_dialog = ' ' * 10
    indent_parenthetical_first = ' ' * 16
    indent_parenthetical_subsequent = ' ' * 17

    fill_parenthetical = 45
    fill_dialog = 45

    top_margin = 1

    def __init__(self, lines):
        self.character = lines[0]
        flipflop = _ParentheticalFlipFlop()
        self.blocks = [
            (paren, ' '.join(t.strip() for t in lines))
            for paren, lines in itertools.groupby(lines[1:], flipflop)]

    def format(self):
        yield self.indent_character + self.character

        for parenthetical, text in self.blocks:
            if parenthetical:
                lines = textwrap.wrap(
                    text,
                    width=self.fill_parenthetical,
                    initial_indent=self.indent_parenthetical_first,
                    subsequent_indent=self.indent_parenthetical_subsequent
                )
            else:
                lines = textwrap.wrap(
                    text,
                    width=self.fill_dialog,
                    initial_indent=self.indent_dialog,
                    subsequent_indent=self.indent_dialog
                )
            for line in lines:
                yield line

class Action(object):
    indent = ''
    fill = 68
    top_margin = 1

    def __init__(self, lines):
        self.text = ' '.join(line.strip() for line in lines)

    def format(self):
        for line in textwrap.wrap(self.text, width=self.fill):
            yield self.indent + line

def is_blank(string):
    return string == '' or string.isspace()

def create_paragraph(line_list):
    if line_list[0].isupper():
        if len(line_list) == 1:
            return Slug(line_list)
        else:
            return Dialog(line_list)
    else:
        return Action(line_list)

def parse(source):
    """Reads raw text input and generates paragraph objects."""
    for blank, lines in itertools.groupby(
        (line.rstrip() for line in source), is_blank
    ):
        if not blank:
            yield create_paragraph(list(lines))

def get_pages(paragraphs):
    """Generates one list of lines per page."""
    lines_on_page = []
    for paragraph in paragraphs:
        top_margin = paragraph.top_margin if lines_on_page else 0
        para_lines = list(paragraph.format())

        if len(lines_on_page) + top_margin + len(para_lines) > lines_per_page:
            yield lines_on_page
            lines_on_page = []
        else:
            lines_on_page += [''] * top_margin
        lines_on_page += para_lines
    yield lines_on_page
