import unittest2
from screenplain import parse
from screenplain.parse import Slug, Action, Dialog, DualDialog, Transition

class ParseTests(unittest2.TestCase):

    # Without this, the @skip decorator gives
    # AttributeError: 'ParseTests' object has no attribute '__name__'
    __name__ = 'ParseTests'

    # A Scene Heading, or "slugline," is any line that has a blank
    # line following it, and either begins with INT or EXT, or has
    # two empty lines preceding it. A Scene Heading always has at
    # least one blank line preceding it.
    # NOTE: Actually the list used in Appendix 1
    def test_slug_with_prefix(self):
        paras = list(parse.parse([
            'INT. SOMEWHERE - DAY',
            '',
            'THIS IS JUST ACTION',
        ]))
        self.assertEquals([Slug, Action], [type(p) for p in paras])

    def test_action_is_not_a_slug(self):
        paras = list(parse.parse([
            '',
            'THIS IS JUST ACTION',
        ]))
        self.assertEquals([Action], [type(p) for p in paras])

    def test_two_lines_creates_a_slug(self):
        types = [type(p) for p in parse.parse([
            '',
            '',
            'This is a slug',
            '',
        ])]
        self.assertEquals([Slug], types)

    # A Character element is any line entirely in caps, with one empty
    # line before it and without an empty line after it.
    def test_all_caps_is_character(self):
        paras = [p for p in parse.parse([
            'SOME GUY',
            'Hello',
        ])]
        self.assertEquals(1, len(paras))
        dialog = paras[0]
        self.assertEquals(Dialog, type(dialog))
        self.assertEquals('SOME GUY', dialog.character)

    # SPMD would not be able to support a character named "23". We
    # might need a syntax to force a character element.
    def test_nonalpha_character(self):
        paras = list(parse.parse([
            '23',
            'Hello',
        ]))
        self.assertEquals([Action], [type(p) for p in paras])

    # See
    # http://prolost.com/storage/downloads/spmd/SPMD_proposal.html#section-br
    def test_twospaced_line_is_not_character(self):
        paras = list(parse.parse([
            'SCANNING THE AISLES...  ',
            'Where is that pit boss?',
        ]))
        self.assertEquals([Action], [type(p) for p in paras])

    def test_simple_parenthetical(self):
        paras = list(parse.parse([
            'STEEL',
            '(starting the engine)',
            'So much for retirement!',
        ]))
        self.assertEquals(1, len(paras))
        dialog = paras[0]
        self.assertEqual(2, len(dialog.blocks))
        self.assertEqual((True, '(starting the engine)'), dialog.blocks[0])
        self.assertEqual((False, 'So much for retirement!'), dialog.blocks[1])

    def test_dual_dialog(self):
        paras = list(parse.parse([
            'BRICK',
            'Fuck retirement.',
            '||',
            'STEEL',
            'Fuck retirement!',
        ]))
        self.assertEquals([DualDialog], [type(p) for p in paras])
        dual = paras[0]
        self.assertEquals('BRICK', dual.left.character)
        self.assertEquals([(False, 'Fuck retirement.')], dual.left.blocks)
        self.assertEquals('STEEL', dual.right.character)
        self.assertEquals([(False, 'Fuck retirement!')], dual.right.blocks)

    def test_standard_transition(self):

        paras = list(parse.parse([
            'Jack begins to argue vociferously in Vietnamese (?)',
            '',
            'CUT TO:',
            '',
            "EXT. BRICK'S POOL - DAY",
        ]))
        self.assertEquals([Action, Transition, Slug], [type(p) for p in paras])

    def test_standard_transition(self):

        paras = list(parse.parse([
            'Jack begins to argue vociferously in Vietnamese (?)',
            '',
            'CUT TO:',
            '',
            "EXT. BRICK'S POOL - DAY",
        ]))
        self.assertEquals([Action, Transition, Slug], [type(p) for p in paras])

    def test_transition_needs_to_be_upper_case(self):
        paras = list(parse.parse([
            'Jack begins to argue vociferously in Vietnamese (?)',
            '',
            'cut to:',
            '',
            "EXT. BRICK'S POOL - DAY",
        ]))
        self.assertEquals([Action, Action, Slug], [type(p) for p in paras])

    def test_not_a_transition_on_trailing_whitespace(self):
        paras = list(parse.parse([
            'Jack begins to argue vociferously in Vietnamese (?)',
            '',
            'CUT TO: ',
            '',
            "EXT. BRICK'S POOL - DAY",
        ]))
        self.assertEquals([Action, Action, Slug], [type(p) for p in paras])

    # Not implemented yet
    @unittest2.expectedFailure
    def test_transition_must_be_followed_by_slug(self):
        paras = list(parse.parse([
            'Bill lights a cigarette.',
            '',
            'CUT TO:',
            '',
            'SOME GUY mowing the lawn.',
        ]))
        self.assertEquals([Action, Action, Action], [type(p) for p in paras])

if __name__ == '__main__':
    unittest2.main()
