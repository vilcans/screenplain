import itertools
import textwrap
import re

# Numbers from http://www.emacswiki.org/emacs/ScreenPlay
# According to http://johnaugust.com/2004/how-many-lines-per-page
lines_per_page = 56

slug_prefixes = (
    'INT. ',
    'EXT. ',
    'INT./EXT. ',
    'INT/EXT. ',
    'INT ',
    'EXT ',
    'INT/EXT ',
    'I/E ',
)

TWOSPACE = ' ' * 2

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
        self.blocks = []  # list of tuples of (is_parenthetical, text)
        self._parse(lines[1:])

    def _parse(self, lines):
        inside_parenthesis = False
        for line in lines:
            if line.startswith('('):
                inside_parenthesis = True
            self.blocks.append((inside_parenthesis, line))
            if line.endswith(')'):
                inside_parenthesis = False

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

class DualDialog(object):
    top_margin = 1

    def __init__(self, left_lines, right_lines):
        self.left = Dialog(left_lines)
        self.right = Dialog(right_lines)

    def format(self):
        # FIXME: I haven't checked yet how dual dialog is supposed to look.
        llines = list(self.left.format())
        rlines = list(self.right.format())
        llines += [''] * (len(rlines) - len(llines))
        rlines += [''] * (len(llines) - len(rlines))
        for left, right in zip(llines, rlines):
            yield '%-34s%s' % (left, right)

class Action(object):
    indent = ''
    fill = 68
    top_margin = 1

    def __init__(self, lines):
        self.text = ' '.join(line.strip() for line in lines)

    def format(self):
        for line in textwrap.wrap(self.text, width=self.fill):
            yield self.indent + line

class Transition(object):
    indent = ''
    fill = 68
    top_margin = 1

    def __init__(self, lines):
        self.text = ' '.join(line.strip() for line in lines)

    def format(self):
        for line in textwrap.wrap(self.text, width=self.fill):
            yield self.indent + line

def is_blank(string):
    return string == '' or string.isspace() and string != '  '

def is_slug(blanks_before, string):
    if blanks_before >= 2:
        return True
    upper = string.upper()
    return any(upper.startswith(s) for s in slug_prefixes)

def _create_dialog(line_list):
    try:
        dual_index = line_list.index('||')
    except ValueError:
        return Dialog(line_list)
    else:
        return DualDialog(line_list[:dual_index], line_list[dual_index + 1:])

def create_paragraph(blanks_before, line_list):
    if is_slug(blanks_before, line_list[0]):
        return Slug(line_list)
    if (
        len(line_list) > 1 and
        line_list[0].isupper() and
        not line_list[0].endswith(TWOSPACE)
    ):
        return _create_dialog(line_list)
    elif len(line_list) == 1 and line_list[0].endswith(':') and line_list[0].isupper():
        # TODO: need to check whether the *next* paragraph is a slug
        # before assuming this is a transition.
        return Transition(line_list)
    else:
        return Action(line_list)

def clean_line(line):
    """Strips leading whitespace and trailing end of line characters in a string.

    Leading whitespace is insignificant in SPMD, and trailing EOL
    appear when reading from a file or HTML form.
    """
    return line.lstrip().rstrip('\r\n')

def parse(source):
    """Reads raw text input and generates paragraph objects."""
    blank_count = 0
    source = (clean_line(line) for line in source)
    for blank, lines in itertools.groupby(source, is_blank):
        if blank:
            blank_count = len(list(lines))
        else:
            yield create_paragraph(blank_count, list(lines))

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
