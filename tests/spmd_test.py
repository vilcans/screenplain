# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import unittest2
from screenplain.parsers.spmd import parse
from screenplain.parsers import spmd
from screenplain.types import (
    Slug, Action, Dialog, DualDialog, Transition, Section
)
from screenplain.richstring import plain, italic, empty_string


class ParseTests(unittest2.TestCase):

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

    def test_two_lines_creates_no_slug(self):
        types = [type(p) for p in parse([
            '',
            '',
            'This is a slug',
            '',
        ])]
        # This used to be Slug. Changed in the Jan 2012 version of the spec.
        self.assertEquals([Action], types)

    def test_period_creates_slug(self):
        paras = parse([
            '.SNIPER SCOPE POV',
            '',
        ])
        self.assertEquals(1, len(paras))
        self.assertEquals(Slug, type(paras[0]))
        self.assertEquals(plain('SNIPER SCOPE POV'), paras[0].line)

    def test_scene_number_is_parsed(self):
        paras = parse(['EXT SOMEWHERE - DAY #42#'])
        self.assertEquals(plain('EXT SOMEWHERE - DAY'), paras[0].line)
        self.assertEquals(plain('42'), paras[0].scene_number)

    def test_only_last_two_hashes_in_slug_used_for_scene_number(self):
        paras = parse(['INT ROOM #237 #42#'])
        self.assertEquals(plain('42'), paras[0].scene_number)
        self.assertEquals(plain('INT ROOM #237'), paras[0].line)

    def test_scene_number_must_be_alphanumeric(self):
        paras = parse(['.SOMEWHERE #*HELLO*#'])
        self.assertIsNone(paras[0].scene_number)
        self.assertEquals(
            (plain)(u'SOMEWHERE #') + (italic)(u'HELLO') + (plain)(u'#'),
            paras[0].line
        )

    def test_section_parsed_correctly(self):
        paras = parse([
            '# first level',
            '',
            '## second level',
        ])
        self.assertEquals([Section, Section], [type(p) for p in paras])
        self.assertEquals(1, paras[0].level)
        self.assertEquals(plain('first level'), paras[0].text)
        self.assertEquals(2, paras[1].level)
        self.assertEquals(plain('second level'), paras[1].text)

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
            '',
            'STEEL ^',
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

    def test_dual_dialog_without_previous_dialog_is_ignored(self):
        paras = list(parse([
            'Brick strolls down the street.',
            '',
            'BRICK ^',
            'Nice retirement.',
        ]))
        self.assertEquals([Action, Dialog], [type(p) for p in paras])
        dialog = paras[1]
        self.assertEqual(plain('BRICK ^'), dialog.character)
        self.assertEqual([
            (False, plain('Nice retirement.'))
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

    def test_transition_does_not_have_to_be_followed_by_slug(self):
        # The "followed by slug" requirement is gone from the Jan 2012 spec
        paras = list(parse([
            'Bill lights a cigarette.',
            '',
            'CUT TO:',
            '',
            'SOME GUY mowing the lawn.',
        ]))
        self.assertEquals(
            [Action, Transition, Action],
            [type(p) for p in paras]
        )

    def test_greater_than_sign_means_transition(self):
        paras = list(parse([
            'Bill blows out the match.',
            '',
            '> FADE OUT.',
            '',
            '.DARKNESS',
        ]))
        self.assertEquals([Action, Transition, Slug], [type(p) for p in paras])
        self.assertEquals(plain('FADE OUT.'), paras[1].line)

    def test_centered_text_is_not_parsed_as_transition(self):
        paras = list(parse([
            'Bill blows out the match.',
            '',
            '> THE END. <',
            '',
            'bye!'
        ]))
        self.assertEquals([Action, Action, Action], [type(p) for p in paras])

    def test_transition_at_end(self):
        paras = list(parse([
            'They stroll hand in hand down the street.',
            '',
            '> FADE OUT.',
        ]))
        self.assertEquals([Action, Transition], [type(p) for p in paras])
        self.assertEquals(plain('FADE OUT.'), paras[1].line)

    def test_action_preserves_leading_whitespace(self):
        paras = list(parse([
            'hello',
            '',
            '  two spaces',
            '   three spaces ',
        ]))
        self.assertEquals([Action, Action], [type(p) for p in paras])
        self.assertEquals(
            [
                plain(u'  two spaces'),
                plain(u'   three spaces'),
            ], paras[1].lines
        )

    def test_leading_and_trailing_spaces_in_dialog(self):
        paras = list(parse([
            'JULIET',
            'O Romeo, Romeo! wherefore art thou Romeo?',
            '  Deny thy father and refuse thy name;  ',
            'Or, if thou wilt not, be but sworn my love,',
            " And I'll no longer be a Capulet.",
        ]))
        self.assertEquals([Dialog], [type(p) for p in paras])
        self.assertEquals([
            (False, plain(u'O Romeo, Romeo! wherefore art thou Romeo?')),
            (False, plain(u'Deny thy father and refuse thy name;')),
            (False, plain(u'Or, if thou wilt not, be but sworn my love,')),
            (False, plain(u"And I'll no longer be a Capulet.")),
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

class TitlePageTests(unittest2.TestCase):

    def test_basic_title_page(self):
        lines = [
            'Title:',
            '    _**BRICK & STEEL**_',
            '    _**FULL RETIRED**_',
            'Author: Stu Maschwitz',
        ]
        self.assertDictEqual(
            {
                'Title': ['_**BRICK & STEEL**_', '_**FULL RETIRED**_'],
                'Author': ['Stu Maschwitz'],
            },
            spmd.parse_title_page(lines)
        )

    def test_multiple_values(self):
        lines = [
            'Title: Death',
            'Title: - a love story',
            'Title:',
            '   (which happens to be true)',
        ]
        self.assertDictEqual(
            {
                'Title': [
                    'Death',
                    '- a love story',
                    '(which happens to be true)'
                ]
            },
            spmd.parse_title_page(lines)
        )

    def test_empty_value_ignored(self):
        lines = [
            'Title:',
            'Author: John August',
        ]
        self.assertDictEqual(
            {'Author': ['John August']},
            spmd.parse_title_page(lines)
        )

    def test_unparsable_title_page_returns_none(self):
        lines = [
            'Title: Inception',
            '    additional line',
        ]
        self.assertIsNone(spmd.parse_title_page(lines))

if __name__ == '__main__':
    unittest2.main()
