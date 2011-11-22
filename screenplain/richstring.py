import re
import cgi

_magic_re = re.compile(u'[\ue700-\ue705]')


class RichString(object):
    """A sequence of segments where each segment can have its own style."""

    def __init__(self, *segments):
        self.segments = tuple(segments)

    def __repr__(self):
        return ' + '.join(repr(s) for s in self.segments)

    def startswith(self, string):
        """Checks if the first segment in this string starts with a
        specific string.

        """
        if '' == string:
            return True
        if not self.segments:
            return False
        return self.segments[0].text.startswith(string)

    def endswith(self, string):
        """Checks if the last segment in this string starts with a
        specific string.

        """
        if '' == string:
            return True
        if not self.segments:
            return False
        return self.segments[-1].text.endswith(string)

    def to_html(self):
        return ''.join(seg.to_html() for seg in self.segments)

    def __eq__(self, other):
        return (
            type(self) == type(other) and
            self.segments == other.segments
        )

    def __ne__(self, other):
        return (
            type(self) != type(other) or
            self.segments != other.segments
        )

    def __add__(self, other):
        if hasattr(other, 'segments'):
            return RichString(*(self.segments + other.segments))
        else:
            raise ValueError('Concatenating requires RichString')

class Segment(object):
    """A piece of a rich string. Has a set of styles."""

    def __init__(self, text, styles):
        """
        Creates a segment with a set of styles.
        text is the raw text string, and 
        styles is a set of Style subclasses"""
        self.styles = set(styles)
        self.text = text

    def __repr__(self):
        return '(%s)(%r)' % (
            '+'.join(
                style.name() for style in self.styles
            ) or 'plain',
            self.text
        )

    def __eq__(self, other):
        return self.text == other.text and self.styles == other.styles

    def __ne__(self, other):
        return self.text != other.text or self.styles != other.styles

    def to_html(self):
        ordered_styles = list(self.styles)
        return (
            ''.join(style.start_html for style in ordered_styles) +
            cgi.escape(self.text) +
            ''.join(style.end_html for style in reversed(ordered_styles))
        )


class Style(object):
    """Abstract base class for styles"""

    start_magic = ''
    end_magic = ''
    start_html = ''
    end_html = ''

    @classmethod
    def name(cls):
        return cls.__name__.lower()


class Italic(Style):

    parse_re = re.compile(
        r'\*'            # one star
        r'([^\s].*?)'        # anything but a space, then text
        r'\*' # finishing with one star
        r'(?!\*)'        # must not be followed by star
    )

    start_magic = u'\ue700'
    end_magic = u'\ue701'

    start_html = '<em>'
    end_html = '</em>'


class Bold(Style):

    parse_re = re.compile(
        r'\*\*'          # two stars
        r'(?=\S)'        # must not be followed by space
        r'(.+?[*_]*)'    # inside text
        r'(?<=\S)\*\*'   # finishing with two stars
    )

    start_magic = u'\ue702'
    end_magic = u'\ue703'

    start_html = '<strong>'
    end_html = '</strong>'


class Underline(Style):

    parse_re =  re.compile(
        r'_'             # underline
        r'(?=\S)'        # must not be followed by space
        r'([^_]+)'       # inside text
        r'(?<=\S)_'      # finishing with underline
    )

    start_magic = u'\ue704'
    end_magic = u'\ue705'

    start_html = '<u>'  # TODO: use an actual html5 tag
    end_html = '</u>'


class _CreateStyledString(object):
    """Function object that creates a RichString object
    with a single segment with a specified style.
    """
    def __init__(self, styles):
        self.styles = styles

    def __call__(self, text):
        return RichString(Segment(text, self.styles))

    def __add__(self, other):
        return _CreateStyledString(self.styles.union(other.styles))

plain = _CreateStyledString(set())
bold = _CreateStyledString(set((Bold,)))
italic = _CreateStyledString(set((Italic,)))
underline = _CreateStyledString((Underline,))


def parse_emphasis(source):
    """Parses emphasis markers like * and ** in a string
    and returns a RichString object.

    >>> parse_emphasis(u'**hello**')
    (bold)(u'hello')
    >>> parse_emphasis(u'plain')
    (plain)(u'plain')
    >>> parse_emphasis(u'**hello** there')
    (bold)(u'hello') + (plain)(u' there')
    """
    source = Bold.parse_re.sub(
        Bold.start_magic + r'\1' + Bold.end_magic, source
    )
    source = Italic.parse_re.sub(
        Italic.start_magic + r'\1' + Italic.end_magic, source
    )
    source = Underline.parse_re.sub(
        Underline.start_magic + r'\1' + Underline.end_magic, source
    )

    styles = set()
    segments = []
    pos = 0

    def append(pos, end):
        if(pos == end):
            return
        text = source[pos:end]
        segments.append(Segment(text, styles))

    for match in _magic_re.finditer(source):
        end = match.start()
        append(pos, end)
        pos = end + 1
        magic = match.group(0)
        if magic == Bold.start_magic:
            styles.add(Bold)
        elif magic == Bold.end_magic:
            styles.remove(Bold)
        elif magic == Italic.start_magic:
            styles.add(Italic)
        elif magic == Italic.end_magic:
            styles.remove(Italic)
        elif magic == Underline.start_magic:
            styles.add(Underline)
        elif magic == Underline.end_magic:
            styles.remove(Underline)
    append(pos, len(source))

    return RichString(*segments)
