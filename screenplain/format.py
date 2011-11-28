# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

# Numbers from http://www.emacswiki.org/emacs/ScreenPlay
# According to http://johnaugust.com/2004/how-many-lines-per-page
lines_per_page = 56


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
