#!/usr/bin/env python

# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import fileinput
import sys
import codecs
from optparse import OptionParser

from screenplain.parsers import fountain

output_formats = (
    'fdx', 'html'
)

usage = """Usage: %prog [options] [input-file [output-file]]

If a file name parameter is missing or a dash (-), input will be read
from standard input and output will be written to standard output.

Screenplain will try to auto-detect the output format if
an output-file is given. Otherwise use the --format option."""


def invalid_format(parser, message):
    parser.error(
        '%s\nUse --format with one of the following formats: %s' %
        (message, ' '.join(output_formats))
    )


def main(args):
    parser = OptionParser(usage=usage)
    parser.add_option(
        '-f', '--format', dest='output_format',
        metavar='FORMAT',
        help=(
            'Set what kind of file to create. FORMAT can be one of ' +
            ', '.join(output_formats)
        )
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
    from screenplain.stationery import list_stationery
    parser.add_option(
        '-s', '--stationery', dest='stationery',
        metavar='STATIONERY',
        help=(
            'For FDX output, choose one of the installed stationery ' +
            'templates below, or specify the absolute path to any ' +
            'properly formatted Final Draft Document. Currently installed ' +
            'stationery: ' +
            ', '.join(list_stationery())
        )
    )
    options, args = parser.parse_args(args)
    if len(args) >= 3:
        parser.error('Too many arguments')
    input_file = (len(args) > 0 and args[0] != '-') and args[0] or None
    output_file = (len(args) > 1 and args[1] != '-') and args[1] or None

    format = options.output_format
    if format is None and output_file:
        if output_file.endswith('.fdx'):
            format = 'fdx'
        elif output_file.endswith('.html'):
            format = 'html'
        else:
            invalid_format(
                parser,
                'Could not detect output format from file name ' + output_file
            )

    if format not in output_formats:
        invalid_format(
            parser, 'Unsupported output format: "%s".' % format
        )

    if input_file:
        input = codecs.open(input_file, 'r', 'utf-8')
    else:
        input = codecs.getreader('utf-8')(sys.stdin)
    screenplay = fountain.parse(input)

    if format == 'pdf':
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
            if format == 'text':
                from screenplain.export.text import to_text
                to_text(screenplay, output)
            elif format == 'fdx':
                from screenplain.export.fdx import to_fdx
                to_fdx(screenplay, output, stationery=options.stationery)
            elif format == 'html':
                from screenplain.export.html import convert
                convert(screenplay, output, bare=options.bare)
        finally:
            if output_file:
                output.close()

if __name__ == '__main__':
    main(sys.argv[1:])
