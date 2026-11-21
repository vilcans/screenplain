# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import io
import os
import xml.etree.ElementTree as ET
import zipfile
from contextlib import contextmanager
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl

from screenplain.richstring import Bold, Italic, Underline, plain
from screenplain.types import (
    Action,
    Dialog,
    DualDialog,
    PageBreak,
    Section,
    Slug,
    Transition,
)

_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "docx_template.docx")

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML_NS = "http://www.w3.org/XML/1998/namespace"

ET.register_namespace("w", W)
ET.register_namespace("r", R)

_EMPTY_ATTRS = AttributesNSImpl({}, {})

_NS_PREFIX = {W: "w", R: "r", XML_NS: "xml"}


def _attrs(*pairs):
    by_name = {(W, k): v for k, v in pairs}
    qnames = {(W, k): f"w:{k}" for k, _ in pairs}
    return AttributesNSImpl(by_name, qnames)


def _xml_attrs(**kwargs):
    by_name = {(XML_NS, k): v for k, v in kwargs.items()}
    qnames = {(XML_NS, k): f"xml:{k}" for k in kwargs}
    return AttributesNSImpl(by_name, qnames)


def _split_tag(tag):
    """Split a '{namespace}local' tag into (namespace, local)."""
    if tag.startswith("{"):
        uri, local = tag[1:].split("}", 1)
        return uri, local
    return None, tag


def _ns_qname(uri, local):
    if uri is None:
        return local
    prefix = _NS_PREFIX.get(uri)
    if prefix is None:
        raise ValueError(
            f"No prefix registered for namespace {uri!r}; "
            "add it to _NS_PREFIX and declare it via startPrefixMapping"
        )
    return f"{prefix}:{local}"


def _emit_element(gen, elem):
    """Emit an ElementTree element and its subtree through the SAX generator."""
    name = _split_tag(elem.tag)
    by_name = {}
    qnames = {}
    for key, value in elem.attrib.items():
        akey = _split_tag(key)
        by_name[akey] = value
        qnames[akey] = _ns_qname(*akey)
    attrs = AttributesNSImpl(by_name, qnames)
    qname = _ns_qname(*name)
    gen.startElementNS(name, qname, attrs)
    if elem.text:
        gen.characters(elem.text)
    for child in elem:
        _emit_element(gen, child)
        if child.tail:
            gen.characters(child.tail)
    gen.endElementNS(name, qname)


def _extract_dual_dialog_xml(template_root):
    """Return the tblPr + tblGrid elements of the table marked by the
    DualDialogTable bookmark, used as the basis for dual dialogue tables."""
    for tbl in template_root.iter(f"{{{W}}}tbl"):
        if any(
            bm.get(f"{{{W}}}name") == "DualDialogTable"
            for bm in tbl.iter(f"{{{W}}}bookmarkStart")
        ):
            found = (tbl.find(f"{{{W}}}tblPr"), tbl.find(f"{{{W}}}tblGrid"))
            return [child for child in found if child is not None]
    raise ValueError("DualDialogTable bookmark not found in template")


class Formatter:
    """Class for converting paragraphs into DOCX XML."""

    def __init__(self, gen, template_root):
        """Initializes the formatter.

        `gen` is an XMLGenerator to write to.
        `template_root` is the parsed template document"""
        self.gen = gen
        self._template_root = template_root
        self._dual_tbl_elems = None
        self._format_functions = {
            Slug: self.format_slug,
            Action: self.format_action,
            Dialog: self.format_dialog,
            DualDialog: self.format_dual,
            Transition: self.format_transition,
            PageBreak: self.format_page_break,
            Section: self.format_section,
        }

    def _dual_table_elements(self):
        """Lazily extract the dual dialogue table grid from the template so
        documents without dual dialogue never touch (or require) it."""
        if self._dual_tbl_elems is None:
            self._dual_tbl_elems = _extract_dual_dialog_xml(self._template_root)
        return self._dual_tbl_elems

    def convert(self, screenplay):
        """Converts a screenplay into DOCX XML and writes it to the generator.
        `screenplay` is a sequence of paragraphs."""
        self._write_title_page(screenplay)
        for para in screenplay:
            format_fn = self._format_functions.get(type(para))
            if format_fn:
                format_fn(para)

    @contextmanager
    def _elem(self, tag, attrs=None):
        self.gen.startElementNS((W, tag), f"w:{tag}", attrs or _EMPTY_ATTRS)
        yield
        self.gen.endElementNS((W, tag), f"w:{tag}")

    def _empty(self, tag, *pairs):
        with self._elem(tag, _attrs(*pairs)):
            pass

    def _write_runs(self, rich_string):
        for segment in rich_string.segments:
            styles = set(segment.get_ordered_styles())
            with self._elem("r"):
                if styles:
                    with self._elem("rPr"):
                        if Bold in styles:
                            self._empty("b")
                        if Italic in styles:
                            self._empty("i")
                        if Underline in styles:
                            self._empty("u", ("val", "single"))
                with self._elem("t", _xml_attrs(space="preserve")):
                    self.gen.characters(segment.text)

    def _write_para(self, style_id, rich_lines, jc=None, ind=None):
        for rich in rich_lines:
            with self._elem("p"):
                with self._elem("pPr"):
                    self._empty("pStyle", ("val", style_id))
                    if jc:
                        self._empty("jc", ("val", jc))
                    if ind is not None:
                        self._empty(
                            "ind", ("left", str(ind[0])), ("right", str(ind[1]))
                        )
                self._write_runs(rich)

    def _write_page_break(self):
        with self._elem("p"):
            with self._elem("r"):
                self._empty("br", ("type", "page"))

    def _write_dialog(self, dialog, cell=False):
        ind = (0, 0) if cell else None
        self._write_para("SPCharacter", [dialog.character], ind=ind)
        for is_parenthetical, line in dialog.blocks:
            style = "SPParenthetical" if is_parenthetical else "SPDialogue"
            self._write_para(style, [line], ind=ind)

    def _write_synopsis(self, synopsis):
        if synopsis:
            self._write_para("SPSynopsis", [plain(synopsis)])

    def _write_title_page(self, screenplay):
        first_centered = True
        first_left = True
        added = False
        for key in _CENTERED_TITLE_KEYS:
            for line in screenplay.get_rich_attribute(key):
                style = (
                    "SPTitlePageCenterFirst" if first_centered else "SPTitlePageCenter"
                )
                self._write_para(style, [line])
                first_centered = False
                added = True
        for key in _LEFT_TITLE_KEYS:
            for line in screenplay.get_rich_attribute(key):
                style = "SPTitlePageLeftFirst" if first_left else "SPTitlePageLeft"
                self._write_para(style, [line])
                first_left = False
                added = True
        if added:
            self._write_page_break()

    def format_slug(self, slug):
        line = slug.line
        if slug.scene_number:
            # Mirror the scene number on both margins, as the other exporters do
            num = slug.scene_number
            line = num + plain("\t") + line + plain("\t") + num
        self._write_para("SPSceneHeading", [line])
        self._write_synopsis(slug.synopsis)

    def format_action(self, para):
        self._write_para("SPAction", para.lines, jc="center" if para.centered else None)

    def format_dialog(self, dialog):
        self._write_dialog(dialog)

    def format_dual(self, dual):
        with self._elem("tbl"):
            for elem in self._dual_table_elements():
                _emit_element(self.gen, elem)
            with self._elem("tr"):
                for dialog in (dual.left, dual.right):
                    with self._elem("tc"):
                        with self._elem("tcPr"):
                            self._empty("tcW", ("w", "0"), ("type", "auto"))
                        self._write_dialog(dialog, cell=True)

    def format_transition(self, para):
        self._write_para("SPTransition", para.lines)

    def format_page_break(self, para):
        self._write_page_break()

    def format_section(self, section):
        # The template defines Heading1..Heading9; clamp into that range.
        level = max(1, min(section.level, 9))
        self._write_para(f"Heading{level}", [section.text])
        self._write_synopsis(section.synopsis)


_CENTERED_TITLE_KEYS = ("Title", "Credit", "Author", "Authors", "Source")
_LEFT_TITLE_KEYS = ("Draft date", "Contact", "Copyright", "Notes")
_TITLE_PAGE_KEYS = _CENTERED_TITLE_KEYS + _LEFT_TITLE_KEYS

# Per the OOXML CT_SectPr schema, pgNumType must precede these child elements.
_SECTPR_AFTER_PGNUM = frozenset(
    f"{{{W}}}{tag}"
    for tag in (
        "cols",
        "formProt",
        "vAlign",
        "noEndnote",
        "titlePg",
        "textDirection",
        "bidi",
        "rtlGutter",
        "docGrid",
    )
)


def _set_page_numbering_start(sect_pr_elem, start):
    """Set pgNumType/@start, inserting pgNumType at its schema-correct
    position (before cols/titlePg/docGrid) if it is not already present."""
    tag = f"{{{W}}}pgNumType"
    pg_num = sect_pr_elem.find(tag)
    if pg_num is None:
        index = len(sect_pr_elem)
        for i, child in enumerate(sect_pr_elem):
            if child.tag in _SECTPR_AFTER_PGNUM:
                index = i
                break
        pg_num = ET.Element(tag)
        sect_pr_elem.insert(index, pg_num)
    pg_num.set(f"{{{W}}}start", start)


def _generate_document_xml(screenplay, template_doc):
    template_root = ET.fromstring(template_doc)
    sect_pr_elem = template_root.find(f".//{{{W}}}sectPr")

    # Start page numbering at 0 so the first script page carries number 1.
    if sect_pr_elem is not None and any(
        screenplay.get_rich_attribute(k) for k in _TITLE_PAGE_KEYS
    ):
        _set_page_numbering_start(sect_pr_elem, "0")

    buf = io.BytesIO()
    gen = XMLGenerator(buf, encoding="utf-8", short_empty_elements=False)
    gen.startDocument()
    gen.startPrefixMapping("w", W)
    gen.startPrefixMapping("r", R)
    gen.startElementNS((W, "document"), "w:document", _EMPTY_ATTRS)
    gen.startElementNS((W, "body"), "w:body", _EMPTY_ATTRS)

    Formatter(gen, template_root).convert(screenplay)

    # sectPr must be the last child of the body
    if sect_pr_elem is not None:
        _emit_element(gen, sect_pr_elem)

    gen.endElementNS((W, "body"), "w:body")
    gen.endElementNS((W, "document"), "w:document")
    gen.endDocument()

    return buf.getvalue()


def to_docx(screenplay, out):
    with zipfile.ZipFile(_TEMPLATE_PATH, "r") as template:
        template_doc = template.read("word/document.xml").decode("utf-8")
        document_xml = _generate_document_xml(screenplay, template_doc)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as output:
            for item in template.infolist():
                if item.filename == "word/document.xml":
                    output.writestr(item, document_xml)
                else:
                    output.writestr(item, template.read(item.filename))
