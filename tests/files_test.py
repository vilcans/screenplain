# Copyright (c) 2012 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from __future__ import with_statement

import unittest2
import tempfile
import os.path
import shutil
import re

from screenplain.main import main

source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))

line_break_re = re.compile('\s*\n\s*')
spaces_re = re.compile('[ \t]+')


def read_file(path):
    with open(path) as stream:
        return stream.read()


def clean_string(s):
    r"""Removes duplicated spaces and line breaks in a string.

    >>> clean_string('foo \n  \nbar\n\n')
    'foo\nbar\n'
    >>> clean_string('foo   bar')
    'foo bar'

    """
    return spaces_re.sub(' ', line_break_re.sub('\n', s))


class ParseTests(unittest2.TestCase):
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

    def test_fountain_to_fdx(self):
        actual, expected = self.convert(
            'simple.fountain', 'simple.fdx', 'simple.fountain.fdx')
        self.assertMultiLineEqual(expected, actual)

    def test_fountain_to_html(self):
        actual, expected = self.convert(
            'simple.fountain', 'simple.html', 'simple.fountain.html', '--bare')
        self.assertMultiLineEqual(expected, actual)

    def test_scene_numbers(self):
        actual, expected = self.convert(
            'scene-numbers.fountain', 'scene-numbers.html',
            'scene-numbers.fountain.html', '--bare')
        self.assertMultiLineEqual(expected, actual)

    def test_sections(self):
        actual, expected = self.convert(
            'sections.fountain', 'sections.html',
            'sections.fountain.html', '--bare')
        self.assertMultiLineEqual(expected, actual)

    def test_boneyard(self):
        actual, expected = self.convert(
            'boneyard.fountain', 'sections.html',
            'boneyard.fountain.html', '--bare')
        self.assertMultiLineEqual(expected, actual)

    def test_page_break(self):
        actual, expected = self.convert(
            'page-break.fountain', 'page-break.html',
            'page-break.fountain.html', '--bare')
        self.assertMultiLineEqual(expected, actual)
