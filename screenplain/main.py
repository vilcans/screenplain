#!/usr/bin/env python

# Run with:
#   PYTHONPATH=. python screenplain/main.py filename.txt

import fileinput
import sys
import codecs
from optparse import OptionParser

from screenplain.parsers.spmd import parse

usage = 'Usage: %prog [options] input-file output-file'

if __name__ == '__main__':
    parser = OptionParser(usage=usage)
    parser.add_option(
        '-f', '--format', dest='output_format',
        metavar='FORMAT',
        help='Set what kind of file to create. FORMAT can be pdf or text.'
    )
    options, args = parser.parse_args()
    if len(args) != 2:
        parser.error('Expected input-file and output-file arguments')
    input_file, output_file = args

    if options.output_format == None:
        if output_file.endswith('.pdf'):
            options.output_format = 'pdf'
        else:
            options.output_format = 'text'

    input = codecs.open(input_file, 'r', 'utf-8')
    screenplay = parse(input)

    if options.output_format == 'text':
        from screenplain.export.text import to_text
        to_text(screenplay, output_file)
    else:
        from screenplain.export.pdf import to_pdf
        to_pdf(screenplay, output_file)
