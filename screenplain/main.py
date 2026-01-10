#!/usr/bin/env python

# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import argparse
import codecs
import sys

from screenplain.parsers import fountain

output_formats = (
    'fdx', 'html', 'pdf'
)

description = """Convert text file to viewable screenplay.

If a file name parameter is missing or a dash (-), input will be read
from standard input and output will be written to standard output.

Screenplain will try to auto-detect the output format if
an output-file is given. Otherwise use the --format option."""


def invalid_format(parser, message):
    formats = " ".join(output_formats)
    parser.error(
        f'{message}\nUse --format with one of the following formats: '
        f'{formats}'
    )


def main(argv):
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input screenplay file (default: stdin)'
    )
    parser.add_argument(
        'output_file',
        nargs='?',
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '-f', '--format',
        dest='output_format',
        metavar='FORMAT',
        help=(
            'Set what kind of file to create. FORMAT can be one of '
            f'{", ".join(output_formats)}'
        )
    )
    parser.add_argument(
        '--bare',
        action='store_true',
        help=(
            'For HTML output, only output the actual screenplay, '
            'not a complete HTML document.'
        )
    )
    parser.add_argument(
        '--css',
        metavar='FILE',
        help=(
            'For HTML output, inline the given CSS file in the HTML document '
            'instead of the default.'
        )
    )
    parser.add_argument(
        '--strong',
        action='store_true',
        help=(
            'For PDF output, scene headings will appear '
            'Bold and Underlined.'
        )
    )
    parser.add_argument(
        '--standard-font',
        action='store_true',
        help=(
            "For PDF output, "
            "use the standard Courier font instead of Courier Prime."
        )
    )
    parser.add_argument(
        '--encoding',
        default='utf-8-sig',
        help="Text encoding of the input file. "
        "Should be one of Python's built-in encodings."
    )
    parser.add_argument(
        '--encoding-errors',
        default='strict',
        choices=['strict', 'ignore', 'replace',
                 'backslashreplace', 'surrogateescape'],
        help='How to handle invalid character codes in the input file'
    )
    args = parser.parse_args(argv)

    # Handle dash as stdin/stdout
    if not args.input_file or args.input_file == '-':
        input_file = None
    else:
        input_file = args.input_file

    if not args.output_file or args.output_file == '-':
        output_file = None
    else:
        output_file = args.output_file

    try:
        codecs.lookup(args.encoding)
    except LookupError:
        parser.error(f'Unknown encoding: {args.encoding}')

    format = args.output_format
    if format is None and output_file:
        if output_file.endswith('.fdx'):
            format = 'fdx'
        elif output_file.endswith('.html'):
            format = 'html'
        elif output_file.endswith('.pdf'):
            format = 'pdf'
        else:
            invalid_format(
                parser,
                f'Could not detect output format from file name {output_file}'
            )

    if format not in output_formats:
        invalid_format(
            parser, f'Unsupported output format: "{format}".'
        )

    if input_file:
        input = codecs.open(
            input_file, 'r',
            encoding=args.encoding,
            errors=args.encoding_errors)
    else:
        input = codecs.getreader(args.encoding)(sys.stdin.buffer)
        input.errors = args.encoding_errors
    screenplay = fountain.parse(input)

    if format == 'pdf':
        output_encoding = None
    else:
        output_encoding = 'utf-8'

    if output_file:
        if output_encoding:
            output = codecs.open(output_file, 'w', output_encoding)
        else:
            output = open(output_file, 'wb')
    else:
        if output_encoding:
            output = codecs.getwriter(output_encoding)(sys.stdout.buffer)
        else:
            output = sys.stdout.buffer

    try:
        if format == 'fdx':
            from screenplain.export.fdx import to_fdx
            to_fdx(screenplay, output)
        elif format == 'html':
            from screenplain.export.html import convert
            convert(
                screenplay, output,
                css_file=args.css, bare=args.bare
            )
        elif format == 'pdf':
            from screenplain.export import pdf
            font_settings = None
            if args.standard_font:
                font_settings = pdf.get_standard_font_settings()
            settings = pdf.Settings(
                font_settings=font_settings, strong_slugs=args.strong
            )
            pdf.to_pdf(screenplay, output, settings=settings)
    finally:
        if output_file:
            output.close()
        if input_file:
            input.close()


def cli():
    """setup.py entry point for console scripts."""
    main(sys.argv[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
