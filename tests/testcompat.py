# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

"""Provides compatibility between Python 2 and 3.

In Python 2 we use the unittest2 module.
The functionality of that module is already in Python 3,
so we don't depend on it.
This module exports the TestCase class from whatever unittest library we have.

"""

try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase
