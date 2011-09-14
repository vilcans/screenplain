import re

_emphasis = re.compile(
    r'(?:'
    r'(\*\*)'        # two stars
    r'(?=\S)'        # must not be followed by space
    r'(.+?[*_]*)'    # inside text
    r'(?<=\S)\*\*'   # finishing with two stars
    r'|'
    r'(\*)'          # one star
    r'(?=\S)'        # must not be followed by space
    r'(.+)'          # inside text
    r'(?<=\S)\*'     # finishing with one star
    r'(?!\*)'        # must not be followed by star
    r'|'
    r'(_)'           # underline
    r'(?=\S)'        # must not be followed by space
    r'([^_]+)'       # inside text
    r'(?<=\S)_'      # finishing with underline
    r')'
)

class RichString(object):
    def __init__(self, *segments):
        self.segments = segments

    def to_html(self):
        result = ''
        for segment in self.segments:
            if isinstance(segment, basestring):
                result += segment
            else:
                result += segment.to_html()
        return result

    def __unicode__(self):
        return self.to_html()

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join(repr(s) for s in self.segments)
        )

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.segments == other.segments
        )

    def __ne__(self, other):
        return (
            self.__class__ != other.__class__ or
            self.segments != other.segments
        )

class Italic(RichString):
    def to_html(self):
        return '<em>' + super(Italic, self).to_html() + '</em>'

class Bold(RichString):
    def to_html(self):
        return '<strong>' + super(Bold, self).to_html() + '</strong>'

class Underline(RichString):
    def to_html(self):
        return '<u>' + super(Underline, self).to_html() + '</u>'

def _parse(source):
    segments = []

    scanner = _emphasis.scanner(source)
    pos = 0
    while pos != len(source):
        match = scanner.search()
        if not match:
            segments.append(source[pos:])
            break
        if match.start() != pos:
            segments.append(source[pos:match.start()])

        (
            two_stars, two_stars_text,
            one_star, one_star_text,
            underline, underline_text
        ) = match.groups()

        if two_stars:
            segments.append(Bold(*_parse(two_stars_text)))
        elif one_star:
            segments.append(Italic(*_parse(one_star_text)))
        else:
            segments.append(Underline(*_parse(underline_text)))
        pos = match.end()

    return segments

def parse_emphasis(source):
    """Parses emphasis markers like * and ** in a string
    and returns a RichString object.
    
    >>> parse_emphasis(u'**hello**')
    Bold(u'hello')
    >>> parse_emphasis(u'plain')
    RichString(u'plain')
    """
    segments = _parse(source)
    if len(segments) == 1 and isinstance(segments[0], RichString):
        return segments[0]
    else:
        return RichString(*segments)
