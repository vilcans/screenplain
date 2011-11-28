# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

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


class DualDialog(object):
    def __init__(self, character1, lines1, character2, lines2):
        self.left = Dialog(character1, lines1)
        self.right = Dialog(character2, lines2)


class Action(object):
    def __init__(self, lines, centered=False):
        self.lines = lines
        self.centered = centered


class Transition(object):
    def __init__(self, line):
        self.line = line

    @property
    def lines(self):
        return [self.line]
