# Copyright (c) 2012 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from __future__ import with_statement

import unittest2
import tempfile
import os.path
import shutil

from screenplain.main import main

source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))

def read_file(path):
    with open(path) as stream:
        return stream.read()


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
        return actual, expected

    def test_spmd_to_fdx(self):
        actual, expected = self.convert(
            'simple.spmd', 'simple.fdx', 'simple.spmd.fdx')
        self.assertMultiLineEqual(expected, actual)

    def test_spmd_to_html(self):
        actual, expected = self.convert(
            'simple.spmd', 'simple.html', 'simple.spmd.html', '--bare')
        self.assertMultiLineEqual(expected, actual)
