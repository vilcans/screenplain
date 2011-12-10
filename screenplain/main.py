#!/usr/bin/env python

# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import fileinput
import sys
import codecs
from optparse import OptionParser

from screenplain.parsers.spmd import parse

output_formats = (
    'fdx', 'html'
)

usage = """Usage: %prog [options] [input-file [output-file]]

If a file name parameter is missing or a dash (-), input will be read
from standard input and output will be written to standard output.

Screenplain will try to auto-detect the output format if
an output-file is given. Otherwise use the --format option."""


def main(args):
    parser = OptionParser(usage=usage)
    parser.add_option(
        '-f', '--format', dest='output_format',
        metavar='FORMAT',
        help=('Set what kind of file to create. FORMAT can be one of '
            + ', '.join(output_formats))
    )
    parser.add_option(
        '--bare',
        action='store_true',
        dest='bare',
        help=(
            'For HTML output, only output the actual screenplay, '
            'not a complete HTML document.'
        )
    )
    options, args = parser.parse_args(args)
    if len(args) >= 3:
        parser.error('Too many arguments')
    input_file = (len(args) > 0 and args[0] != '-') and args[0] or None
    output_file = (len(args) > 1 and args[1] != '-') and args[1] or None

    if options.output_format == None and output_file:
        if output_file.endswith('.fdx'):
            options.output_format = 'fdx'
        elif output_file.endswith('.html'):
            options.output_format = 'html'
        else:
            options.output_format = 'text'

    if options.output_format not in output_formats:
        parser.error(
            'Could not detect output format.\n'
            'Use --format with one of the following formats: ' +
            ' '.join(output_formats))

    if input_file:
        input = codecs.open(input_file, 'r', 'utf-8')
    else:
        input = codecs.getreader('utf-8')(sys.stdin)
    screenplay = parse(input)

    if options.output_format == 'pdf':
        from screenplain.export.pdf import to_pdf
        if not output_file:
            sys.stderr.write("Can't write PDF to standard output")
            sys.exit(2)
        to_pdf(screenplay, output_file)
    else:
        if output_file:
            output = codecs.open(output_file, 'w', 'utf-8')
        else:
            output = codecs.getwriter('utf-8')(sys.stdout)
        try:
            if options.output_format == 'text':
                from screenplain.export.text import to_text
                to_text(screenplay, output)
            elif options.output_format == 'fdx':
                from screenplain.export.fdx import to_fdx
                to_fdx(screenplay, output)
            elif options.output_format == 'html':
                from screenplain.export.html import convert
                convert(screenplay, output, bare=options.bare)
        finally:
            if output_file:
                output.close()

if __name__ == '__main__':
    main(sys.argv[1:])
