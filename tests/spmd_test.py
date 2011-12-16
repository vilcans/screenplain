# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import unittest2
from screenplain.parsers.spmd import parse
from screenplain.types import Slug, Action, Dialog, DualDialog, Transition
from screenplain.richstring import plain, empty_string


class ParseTests(unittest2.TestCase):

    # A Scene Heading, or "slugline," is any line that has a blank
    # line following it, and either begins with INT or EXT, or has
    # two empty lines preceding it. A Scene Heading always has at
    # least one blank line preceding it.
    # NOTE: Actually the list used in Appendix 1
    def test_slug_with_prefix(self):
        paras = list(parse([
            'INT. SOMEWHERE - DAY',
            '',
            'THIS IS JUST ACTION',
        ]))
        self.assertEquals([Slug, Action], [type(p) for p in paras])

    def test_slug_must_be_single_line(self):
        paras = list(parse([
            'INT. SOMEWHERE - DAY',
            'ANOTHER LINE',
            '',
            'Some action',
        ]))
        self.assertEquals([Dialog, Action], [type(p) for p in paras])
        # What looks like a scene headingis parsed as a character name.
        # Unexpected perhaps, but that's how I interpreted the spec.
        self.assertEquals(plain('INT. SOMEWHERE - DAY'), paras[0].character)
        self.assertEquals([plain('Some action')], paras[1].lines)

    def test_action_is_not_a_slug(self):
        paras = list(parse([
            '',
            'THIS IS JUST ACTION',
        ]))
        self.assertEquals([Action], [type(p) for p in paras])

    def test_two_lines_creates_a_slug(self):
        types = [type(p) for p in parse([
            '',
            '',
            'This is a slug',
            '',
        ])]
        self.assertEquals([Slug], types)

    # A Character element is any line entirely in caps, with one empty
    # line before it and without an empty line after it.
    def test_all_caps_is_character(self):
        paras = [p for p in parse([
            'SOME GUY',
            'Hello',
        ])]
        self.assertEquals(1, len(paras))
        dialog = paras[0]
        self.assertEquals(Dialog, type(dialog))
        self.assertEquals(plain('SOME GUY'), dialog.character)

    # SPMD would not be able to support a character named "23". We
    # might need a syntax to force a character element.
    def test_nonalpha_character(self):
        paras = list(parse([
            '23',
            'Hello',
        ]))
        self.assertEquals([Action], [type(p) for p in paras])

    # See
    # http://prolost.com/storage/downloads/spmd/SPMD_proposal.html#section-br
    def test_twospaced_line_is_not_character(self):
        paras = list(parse([
            'SCANNING THE AISLES...  ',
            'Where is that pit boss?',
        ]))
        self.assertEquals([Action], [type(p) for p in paras])

    def test_simple_parenthetical(self):
        paras = list(parse([
            'STEEL',
            '(starting the engine)',
            'So much for retirement!',
        ]))
        self.assertEquals(1, len(paras))
        dialog = paras[0]
        self.assertEqual(2, len(dialog.blocks))
        self.assertEqual(
            (True, plain('(starting the engine)')),
            dialog.blocks[0]
        )
        self.assertEqual(
            (False, plain('So much for retirement!')),
            dialog.blocks[1]
        )

    def test_twospace_keeps_dialog_together(self):
        paras = list(parse([
            'SOMEONE',
            'One',
            '  ',
            'Two',
        ]))
        self.assertEquals([Dialog], [type(p) for p in paras])
        self.assertEquals([
            (False, plain('One')),
            (False, empty_string),
            (False, plain('Two')),
        ], paras[0].blocks)

    def test_dual_dialog(self):
        paras = list(parse([
            'BRICK',
            'Fuck retirement.',
            '||',
            'STEEL',
            'Fuck retirement!',
        ]))
        self.assertEquals([DualDialog], [type(p) for p in paras])
        dual = paras[0]
        self.assertEquals(plain('BRICK'), dual.left.character)
        self.assertEquals(
            [(False, plain('Fuck retirement.'))],
            dual.left.blocks
        )
        self.assertEquals(plain('STEEL'), dual.right.character)
        self.assertEquals(
            [(False, plain('Fuck retirement!'))],
            dual.right.blocks
        )

    def test_dual_dialog_with_empty_right_dialog_is_ordinary_dialog(self):
        paras = list(parse([
            'BRICK',
            'Nice retirement.',
            '||',
        ]))
        self.assertEquals([Dialog], [type(p) for p in paras])
        dialog = paras[0]
        self.assertEqual(plain('BRICK'), dialog.character)
        self.assertEqual([
            (False, plain('Nice retirement.')),
            (False, plain('||'))
        ], dialog.blocks)

    def test_standard_transition(self):

        paras = list(parse([
            'Jack begins to argue vociferously in Vietnamese (?)',
            '',
            'CUT TO:',
            '',
            "EXT. BRICK'S POOL - DAY",
        ]))
        self.assertEquals([Action, Transition, Slug], [type(p) for p in paras])

    def test_transition_needs_to_be_upper_case(self):
        paras = list(parse([
            'Jack begins to argue vociferously in Vietnamese (?)',
            '',
            'cut to:',
            '',
            "EXT. BRICK'S POOL - DAY",
        ]))
        self.assertEquals([Action, Action, Slug], [type(p) for p in paras])

    def test_not_a_transition_on_trailing_whitespace(self):
        paras = list(parse([
            'Jack begins to argue vociferously in Vietnamese (?)',
            '',
            'CUT TO: ',
            '',
            "EXT. BRICK'S POOL - DAY",
        ]))
        self.assertEquals([Action, Action, Slug], [type(p) for p in paras])

    def test_transition_must_be_followed_by_slug(self):
        paras = list(parse([
            'Bill lights a cigarette.',
            '',
            'CUT TO:',
            '',
            'SOME GUY mowing the lawn.',
        ]))
        self.assertEquals([Action, Action, Action], [type(p) for p in paras])

    def test_multiline_paragraph(self):
        """Check that we don't join lines like Markdown does.
        """
        paras = list(parse([
            'They drink long and well from the beers.',
            '',
            "And then there's a long beat.",
            "Longer than is funny. ",
            "   Long enough to be depressing.",
            '',
            'The men look at each other.',
        ]))
        self.assertEquals([Action, Action, Action], [type(p) for p in paras])
        self.assertEquals(
            [
                plain("And then there's a long beat."),
                plain("Longer than is funny."),
                plain("Long enough to be depressing."),
            ], paras[1].lines
        )

    def test_multiline_dialog(self):
        paras = list(parse([
            'JULIET',
            'O Romeo, Romeo! wherefore art thou Romeo?',
            '  Deny thy father and refuse thy name;  ',
            'Or, if thou wilt not, be but sworn my love,',
            " And I'll no longer be a Capulet.",
        ]))
        self.assertEquals([Dialog], [type(p) for p in paras])
        self.assertEquals([
            (False, plain('O Romeo, Romeo! wherefore art thou Romeo?')),
            (False, plain('Deny thy father and refuse thy name;')),
            (False, plain('Or, if thou wilt not, be but sworn my love,')),
            (False, plain("And I'll no longer be a Capulet.")),
        ], paras[0].blocks)

    def test_single_centered_line(self):
        paras = list(parse(['> center me! <']))
        self.assertEquals([Action], [type(p) for p in paras])
        self.assertTrue(paras[0].centered)

    def test_full_centered_paragraph(self):
        lines = [
            '> first! <',
            '  > second!   <',
            '> third!< ',
        ]
        paras = list(parse(lines))
        self.assertEquals([Action], [type(p) for p in paras])
        self.assertTrue(paras[0].centered)
        self.assertEquals([
            plain('first!'),
            plain('second!'),
            plain('third!'),
        ], paras[0].lines)

    def test_upper_case_centered_not_parsed_as_dialog(self):
        paras = list(parse([
            '> FIRST! <',
            '  > SECOND! <',
            '> THIRD! <',
        ]))
        self.assertEquals([Action], [type(p) for p in paras])
        self.assertTrue(paras[0].centered)

    def test_centering_marks_in_middle_of_paragraphs_are_verbatim(self):
        lines = [
            'first!',
            '> second! <',
            'third!',
        ]
        paras = list(parse(lines))
        self.assertEquals([Action], [type(p) for p in paras])
        self.assertFalse(paras[0].centered)
        self.assertEquals([plain(line) for line in lines], paras[0].lines)

if __name__ == '__main__':
    unittest2.main()
