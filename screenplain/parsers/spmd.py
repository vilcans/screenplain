# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import itertools
import re

from screenplain.types import (
    Slug, Action, Dialog, DualDialog, Transition
)
from screenplain.richstring import parse_emphasis

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

centered_re = re.compile(r'\s*>\s*(.*)\s*<\s*$')


def is_blank(string):
    return string == '' or string.isspace() and string != TWOSPACE


def is_slug(blanks_before, line_list):
    if len(line_list) != 1:
        return False
    if blanks_before >= 2:
        return True
    upper = line_list[0].upper()
    return any(upper.startswith(s) for s in slug_prefixes)


def _create_dialog(line_list):
    dual_index = None
    try:
        dual_index = line_list.index('||', 0, len(line_list) - 1)
    except ValueError:
        return Dialog(
            parse_emphasis(line_list[0]),
            _to_rich(line_list[1:])
        )
    else:
        return DualDialog(
            # character1
            parse_emphasis(line_list[0].strip()),
            # lines1
            _to_rich(line_list[1:dual_index]),
            # character2
            parse_emphasis(line_list[dual_index + 1].strip()),
            # lines2
            _to_rich(line_list[dual_index + 2:])
        )


def _to_rich(line_list):
    """Converts a line list into a list of RichString."""
    return [parse_emphasis(line.strip()) for line in line_list]


def create_paragraph(blanks_before, line_list):
    first_line = line_list[0]
    if is_slug(blanks_before, line_list):
        return Slug(_to_rich(line_list)[0])
    elif all(centered_re.match(line) for line in line_list):
        return Action(_to_rich(
            centered_re.match(line).group(1) for line in line_list
        ), centered=True)
    elif (
        len(line_list) > 1 and
        first_line.isupper() and
        not first_line.endswith(TWOSPACE)
    ):
        return _create_dialog(line_list)
    elif (
        len(line_list) == 1 and first_line.isupper()
        and (first_line.endswith(':') or first_line.startswith('>'))
    ):
        # Assume this is a transition. It may be changed to Action
        # later if we find that it's not followed by a slug.
        if first_line.startswith('>'):
            return Transition(_to_rich([first_line[1:]])[0])
        else:
            return Transition(_to_rich([first_line])[0])
    else:
        return Action(_to_rich(line_list))


def clean_line(line):
    """Strips leading whitespace and trailing end of line characters
    in a string.

    Leading whitespace is insignificant in SPMD, and trailing EOL
    appear when reading from a file or HTML form.
    """
    stripped = line.rstrip('\r\n')
    if line == '  ':
        return line
    return line.lstrip()


def parse(source):
    """Reads raw text input and generates paragraph objects."""
    blank_count = 0
    source = (clean_line(line) for line in source)
    paragraphs = []
    for blank, lines in itertools.groupby(source, is_blank):
        if blank:
            blank_count = len(list(lines))
        else:
            paragraphs.append(create_paragraph(blank_count, list(lines)))

    # Make a second pass over the script and replace transitions not
    # followed by sluglines with action.
    for i in xrange(len(paragraphs) - 1):
        if (isinstance(paragraphs[i], Transition) and
            not isinstance(paragraphs[i + 1], Slug)):
            paragraphs[i] = Action(paragraphs[i].lines)
    return paragraphs
