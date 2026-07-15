# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

"""Minimal DOCX reader for tests.

A .docx file is a zip of XML parts.  This module reads just enough of the
WordprocessingML structure (paragraphs, runs, styles and tables) to let the
tests inspect generated documents without depending on python-docx.
"""

import re
import xml.etree.ElementTree as ET
import zipfile

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

_HEADING_NAME = re.compile(r"^heading (\d)$")


def _q(tag):
    return f"{{{W}}}{tag}"


def _toggle(rpr, tag):
    """Read an on/off run property such as <w:b/> the way python-docx does:
    True if present and enabled, False if explicitly disabled, None if absent.
    """
    if rpr is None:
        return None
    el = rpr.find(_q(tag))
    if el is None:
        return None
    val = el.get(_q("val"))
    if val in ("false", "0", "off", "none"):
        return False
    return True


class Run:
    def __init__(self, r_elem):
        self._r = r_elem

    @property
    def text(self):
        return "".join(t.text or "" for t in self._r.iter(_q("t")))

    @property
    def _rpr(self):
        return self._r.find(_q("rPr"))

    @property
    def bold(self):
        return _toggle(self._rpr, "b")

    @property
    def italic(self):
        return _toggle(self._rpr, "i")

    @property
    def underline(self):
        return _toggle(self._rpr, "u")


class Paragraph:
    def __init__(self, p_elem, styles):
        self._p = p_elem
        self._styles = styles

    @property
    def _ppr(self):
        return self._p.find(_q("pPr"))

    @property
    def style_id(self):
        ppr = self._ppr
        if ppr is None:
            return None
        ps = ppr.find(_q("pStyle"))
        return ps.get(_q("val")) if ps is not None else None

    @property
    def style_name(self):
        sid = self.style_id
        if sid is None:
            return "Normal"
        return self._styles.get(sid, sid)

    @property
    def text(self):
        return "".join(t.text or "" for t in self._p.iter(_q("t")))

    @property
    def runs(self):
        return [Run(r) for r in self._p.findall(_q("r"))]

    @property
    def alignment(self):
        ppr = self._ppr
        if ppr is None:
            return None
        jc = ppr.find(_q("jc"))
        return jc.get(_q("val")) if jc is not None else None

    @property
    def xml(self):
        return ET.tostring(self._p, encoding="unicode")


class Cell:
    def __init__(self, tc_elem, styles):
        self._tc = tc_elem
        self._styles = styles

    @property
    def paragraphs(self):
        return [Paragraph(p, self._styles) for p in self._tc.findall(_q("p"))]


class Row:
    def __init__(self, tr_elem, styles):
        self._tr = tr_elem
        self._styles = styles

    @property
    def cells(self):
        return [Cell(tc, self._styles) for tc in self._tr.findall(_q("tc"))]


class Table:
    def __init__(self, tbl_elem, styles):
        self._tbl = tbl_elem
        self._styles = styles

    @property
    def rows(self):
        return [Row(tr, self._styles) for tr in self._tbl.findall(_q("tr"))]

    @property
    def columns(self):
        grid = self._tbl.find(_q("tblGrid"))
        return grid.findall(_q("gridCol")) if grid is not None else []


def _parse_styles(styles_xml):
    """Map styleId -> human-readable style name from word/styles.xml."""
    mapping = {}
    if not styles_xml:
        return mapping
    root = ET.fromstring(styles_xml)
    for style in root.findall(_q("style")):
        sid = style.get(_q("styleId"))
        if sid is None:
            continue
        name_el = style.find(_q("name"))
        name = name_el.get(_q("val")) if name_el is not None else sid
        # Word stores built-in heading styles under the internal name "heading N"
        heading = _HEADING_NAME.match(name)
        if heading:
            name = f"Heading {heading.group(1)}"
        mapping[sid] = name
    return mapping


class Document:
    """Reads a .docx from a path or file-like object."""

    def __init__(self, source):
        with zipfile.ZipFile(source) as z:
            doc_xml = z.read("word/document.xml")
            try:
                styles_xml = z.read("word/styles.xml")
            except KeyError:
                styles_xml = None
        self._styles = _parse_styles(styles_xml)
        self._body = ET.fromstring(doc_xml).find(_q("body"))

    @property
    def body_items(self):
        """Top-level paragraphs and tables in document order."""
        items = []
        for el in self._body:
            if el.tag == _q("p"):
                items.append(Paragraph(el, self._styles))
            elif el.tag == _q("tbl"):
                items.append(Table(el, self._styles))
        return items

    @property
    def paragraphs(self):
        return [i for i in self.body_items if isinstance(i, Paragraph)]

    @property
    def tables(self):
        return [i for i in self.body_items if isinstance(i, Table)]
