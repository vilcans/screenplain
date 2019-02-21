"""Runs nosetest after preparing the test cases.

Removes the leading u from unicode literals so
Python 3 doctests won't fail.

"""

from screenplain import richstring
import re

unicode_literal = re.compile(r'u([\'"])')

for n in (
    'parse_emphasis',
    '_unescape',
    '_demagic_literals',
):
    attr = getattr(richstring, n)
    old_doc = getattr(attr, '__doc__')
    new_doc = unicode_literal.sub(r'\1', old_doc)
    setattr(attr, '__doc__', new_doc)

import nose
nose.main(argv='nosetests --nocapture --with-doctest --doctest-tests'.split())
