import textwrap


class Slug(object):
    indent = ''
    top_margin = 1

    def __init__(self, line):
        self.line = line

    @property
    def lines(self):
        return [self.line]


class Dialog(object):
    indent_character = ' ' * 22
    indent_dialog = ' ' * 10
    indent_parenthetical_first = ' ' * 16
    indent_parenthetical_subsequent = ' ' * 17

    fill_parenthetical = 45
    fill_dialog = 45

    top_margin = 1

    def __init__(self, character, lines):
        self.character = character
        self.blocks = []  # list of tuples of (is_parenthetical, text)
        self._parse(lines)

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

    def __init__(self, character1, lines1, character2, lines2):
        self.left = Dialog(character1, lines1)
        self.right = Dialog(character2, lines2)

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

    def __init__(self, lines, centered=False):
        self.lines = lines
        self.centered = centered

    def format(self):
        for logical_line in self.lines:
            for line in textwrap.wrap(logical_line, width=self.fill):
                yield self.indent + line


class Transition(object):
    indent = ''
    fill = 68
    top_margin = 1

    def __init__(self, line):
        self.line = line

    @property
    def lines(self):
        return [self.line]

    def format(self):
        for logical_line in self.lines:
            for line in textwrap.wrap(logical_line, width=self.fill):
                yield self.indent + line
