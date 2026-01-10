# Copyright (c) 2012 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import os
import os.path
import re
import shutil
import tempfile
from unittest import TestCase

from screenplain.main import main

source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))

line_break_re = re.compile('\\s*\n\\s*')
spaces_re = re.compile('[ \t]+')


def read_file(path):
    with open(path, encoding="utf-8") as stream:
        return stream.read()


def clean_string(s):
    r"""Removes duplicated spaces and line breaks in a string.

    >>> clean_string('foo \n  \nbar\n\n')
    'foo\nbar\n'
    >>> clean_string('foo   bar')
    'foo bar'

    """
    return spaces_re.sub(' ', line_break_re.sub('\n', s))


class FileTests(TestCase):
    """High level tests that runs Screenplain using command line arguments.
    """

    maxDiff = None

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def source(self, filename):
        return os.path.join(source_dir, filename)

    def target(self, name):
        return os.path.join(self.dir, name)

    def convert(
        self,
        input_file, output_file, expected_results_file,
        *options
    ):
        input_path = self.source(input_file)
        output_path = self.target(output_file)
        main(list(options) + [input_path, output_path])
        actual = read_file(output_path)
        expected = read_file(self.source(expected_results_file))
        return clean_string(actual), clean_string(expected)

    @classmethod
    def add_file_case(cls, source_file, expected_results_file):
        """Add a test case that compares the content
        of a generated file with the expected results.

        """
        base, _ = os.path.splitext(source_file)
        extension = os.path.splitext(expected_results_file)[1][1:]

        def test_function(self):
            actual, expected = self.convert(
                source_file, base + '.' + extension,
                expected_results_file,
                '--bare'
            )
            self.assertMultiLineEqual(expected, actual)

        func_name = (
            'test_' +
            source_file.replace('.', '_') +
            '_to_' +
            extension
        )
        setattr(cls, func_name, test_function)


def _create_tests():
    """Creates a test case for every source/expect file pair.

    Finds all the source files in the test files directory.
    (A source file is one with the .fountain extension,
    e.g. 'foo.fountain'.)
    For each of them, finds the corresponding expect files.
    (An expect file has another extension, e.g. 'foo.html'
    which contains the expected output when converting foo.fountain
    to HTML.)
    Skips expect files that are for PDF output (i.e. end with .pdf),
    as they are handled by visual/pdf_test.py.
    """
    test_files = os.listdir(source_dir)
    source_files = [f for f in test_files if f.endswith('.fountain')]
    expect_files = [
        f for f in test_files
        if not f.endswith('.fountain') and not f.endswith('.pdf')
    ]

    for source in source_files:
        base = os.path.splitext(source)[0] + '.'
        for expected in (
            f for f in expect_files if f.startswith(base)
        ):
            FileTests.add_file_case(source, expected)


_create_tests()
