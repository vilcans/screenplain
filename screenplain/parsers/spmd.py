# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import itertools
import re

from screenplain.types import (
    Slug, Action, Dialog, DualDialog, Transition
)
from screenplain.richstring import parse_emphasis, plain

slug_regexes = (
    re.compile(r'^(INT|EXT|EST)[ .]'),
    re.compile(r'^(INT\.?/EXT\.?)[ .]'),
    re.compile(r'^I/E[ .]'),
)

TWOSPACE = ' ' * 2

centered_re = re.compile(r'\s*>\s*(.*?)\s*<\s*$')
dual_dialog_re = re.compile(r'^(.+?)(\s*\^)$')
slug_re = re.compile(r'(?:(\.)\s*)?(\S.*?)\s*$')
scene_number_re = re.compile(r'(.*?)\s*(?:#([\w\-.]+)#)\s*$')
transition_re = re.compile(r'(>?)\s*(.+?)(:?)$')


def _to_rich(line_or_line_list):
    """Converts a line list into a list of RichString
    or a single string to a RichString.

    """
    if isinstance(line_or_line_list, basestring):
        return parse_emphasis(line_or_line_list)
    else:
        return [parse_emphasis(line) for line in line_or_line_list]


class InputParagraph(object):
    def __init__(self, lines):
        self.lines = lines

    def update_list(self, previous_paragraphs):
        """Inserts this paragraph into a list.
        Modifies the `previous_paragraphs` list.
        """
        previous_paragraphs.append(
            self.as_slug() or
            self.as_centered_action() or
            self.as_dialog(previous_paragraphs) or
            self.as_transition() or
            self.as_action()
        )

    def as_slug(self):
        if len(self.lines) != 1:
            return None

        match = slug_re.match(self.lines[0])
        if not match:
            return None

        period, text = match.groups()
        text = text.upper()
        if not period and not any(regex.match(text) for regex in slug_regexes):
            return None

        match = scene_number_re.match(text)
        if match:
            text, scene_number = match.groups()
            return Slug(_to_rich(text), plain(scene_number))
        else:
            return Slug(_to_rich(text))

    def as_centered_action(self):
        if not all(centered_re.match(line) for line in self.lines):
            return None
        return Action(_to_rich(
            centered_re.match(line).group(1) for line in self.lines
        ), centered=True)

    def _create_dialog(self, character):
        return Dialog(
            parse_emphasis(character),
            _to_rich(line.strip() for line in self.lines[1:])
        )

    def as_dialog(self, previous_paragraphs):
        if len(self.lines) < 2:
            return None

        character = self.lines[0]
        if not character.isupper() or character.endswith(TWOSPACE):
            return None

        if previous_paragraphs and isinstance(previous_paragraphs[-1], Dialog):
            dual_match = dual_dialog_re.match(character)
            if dual_match:
                previous = previous_paragraphs.pop()
                dialog = self._create_dialog(dual_match.group(1))
                return DualDialog(previous, dialog)

        return self._create_dialog(character)

    def as_transition(self):
        if len(self.lines) != 1:
            return None

        match = transition_re.match(self.lines[0])
        if not match:
            return None
        greater_than, text, colon = match.groups()

        if greater_than:
            return Transition(_to_rich(text.upper() + colon))

        if text.isupper() and colon:
            return Transition(_to_rich(text + colon))

        return None

    def as_action(self):
        return Action(_to_rich(line.rstrip() for line in self.lines))


def _preprocess_line(raw_line):
    r"""Replaces tabs with spaces and removes trailing end of line markers.

    >>> _preprocess_line('foo \r\n\n')
    'foo '

    """
    return raw_line.expandtabs(4).rstrip('\r\n')


def _is_blank(line):
    return line == ''


def parse(source):
    """Reads raw text input and generates paragraph objects."""
    source = (_preprocess_line(line) for line in source)
    paragraphs = []
    for blank, input_lines in itertools.groupby(source, _is_blank):
        if not blank:
            paragraph = InputParagraph(list(input_lines))
            paragraph.update_list(paragraphs)

    return paragraphs
