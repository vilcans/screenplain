# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from io import StringIO
from unittest import TestCase

from screenplain.parsers import fountain
from screenplain.richstring import empty_string, italic, plain
from screenplain.types import (
    Action,
    Dialog,
    DualDialog,
    PageBreak,
    Section,
    Slug,
    Transition,
)


def parse(lines):
    content = '\n'.join(lines)
    return list(fountain.parse(StringIO(content)))


class SlugTests(TestCase):
    def test_slug_with_prefix(self):
        paras = parse([
            'INT. SOMEWHERE - DAY',
            '',
            'THIS IS JUST ACTION',
        ])
        self.assertEqual([Slug, Action], [type(p) for p in paras])

    def test_slug_must_be_single_line(self):
        paras = parse([
            'INT. SOMEWHERE - DAY',
            'ANOTHER LINE',
            '',
            'Some action',
        ])
        self.assertEqual([Dialog, Action], [type(p) for p in paras])
        # What looks like a scene headingis parsed as a character name.
        # Unexpected perhaps, but that's how I interpreted the spec.
        self.assertEqual(plain('INT. SOMEWHERE - DAY'), paras[0].character)
        self.assertEqual([plain('Some action')], paras[1].lines)

    def test_action_is_not_a_slug(self):
        paras = parse([
            '',
            'THIS IS JUST ACTION',
        ])
        self.assertEqual([Action], [type(p) for p in paras])

    def test_two_lines_creates_no_slug(self):
        types = [type(p) for p in parse([
            '',
            '',
            'This is a slug',
            '',
        ])]
        # This used to be Slug. Changed in the Jan 2012 version of the spec.
        self.assertEqual([Action], types)

    def test_period_creates_slug(self):
        paras = parse([
            '.SNIPER SCOPE POV',
            '',
        ])
        self.assertEqual(1, len(paras))
        self.assertEqual(Slug, type(paras[0]))
        self.assertEqual(plain('SNIPER SCOPE POV'), paras[0].line)

    def test_more_than_one_period_does_not_create_slug(self):
        paras = parse([
            '..AND THEN...',
            '',
        ])
        self.assertEqual(1, len(paras))
        self.assertEqual(Action, type(paras[0]))
        self.assertEqual(plain('..AND THEN...'), paras[0].lines[0])

    def test_scene_number_is_parsed(self):
        paras = parse(['EXT SOMEWHERE - DAY #42#'])
        self.assertEqual(plain('EXT SOMEWHERE - DAY'), paras[0].line)
        self.assertEqual(plain('42'), paras[0].scene_number)

    def test_only_last_two_hashes_in_slug_used_for_scene_number(self):
        paras = parse(['INT ROOM #237 #42#'])
        self.assertEqual(plain('42'), paras[0].scene_number)
        self.assertEqual(plain('INT ROOM #237'), paras[0].line)

    def test_scene_number_must_be_alphanumeric(self):
        paras = parse(['.SOMEWHERE #*HELLO*#'])
        self.assertIsNone(paras[0].scene_number)
        self.assertEqual(
            (plain)('SOMEWHERE #') + (italic)('HELLO') + (plain)('#'),
            paras[0].line
        )


class SectionTests(TestCase):
    def test_section_parsed_correctly(self):
        paras = parse([
            '# first level',
            '',
            '## second level',
        ])
        self.assertEqual([Section, Section], [type(p) for p in paras])
        self.assertEqual(1, paras[0].level)
        self.assertEqual(plain('first level'), paras[0].text)
        self.assertEqual(2, paras[1].level)
        self.assertEqual(plain('second level'), paras[1].text)

    def test_multiple_sections_in_one_paragraph(self):
        paras = parse([
            '# first level',
            '## second level',
            '# first level again'
        ])
        self.assertEqual(
            [Section, Section, Section],
            [type(p) for p in paras]
        )
        self.assertEqual(1, paras[0].level)
        self.assertEqual(plain('first level'), paras[0].text)
        self.assertEqual(2, paras[1].level)
        self.assertEqual(plain('second level'), paras[1].text)
        self.assertEqual(1, paras[2].level)
        self.assertEqual(plain('first level again'), paras[2].text)

    def test_multiple_sections_with_synopsis(self):
        paras = parse([
            '# first level',
            '= level one synopsis',
            '## second level',
        ])
        self.assertEqual([
            Section(plain('first level'), 1, 'level one synopsis'),
            Section(plain('second level'), 2, None),
        ], paras)


class DialogTests(TestCase):
    # A Character element is any line entirely in caps, with one empty
    # line before it and without an empty line after it.
    def test_all_caps_is_character(self):
        paras = [p for p in parse([
            'SOME GUY',
            'Hello',
        ])]
        self.assertEqual(1, len(paras))
        dialog = paras[0]
        self.assertEqual(Dialog, type(dialog))
        self.assertEqual(plain('SOME GUY'), dialog.character)

    def test_alphanumeric_character(self):
        paras = parse([
            'R2D2',
            'Bee-bop',
        ])
        self.assertEqual([Dialog], [type(p) for p in paras])
        self.assertEqual(plain('R2D2'), paras[0].character)

    # Spec http://fountain.io/syntax#section-character:
    # Character names must include at least one alphabetical character.
    # "R2D2" works, but "23" does not.
    def test_nonalpha_character(self):
        paras = parse([
            '23',
            'Hello',
        ])
        self.assertEqual([Action], [type(p) for p in paras])

    # Spec http://fountain.io/syntax#section-character:
    # You can force a Character element by preceding it with the "at" symbol @.
    def test_at_sign_forces_dialog(self):
        paras = parse([
            '@McCLANE',
            'Yippee ki-yay',
        ])
        self.assertEqual([Dialog], [type(p) for p in paras])
        self.assertEqual(plain('McCLANE'), paras[0].character)

    def test_twospaced_line_is_not_character(self):
        paras = parse([
            'SCANNING THE AISLES...  ',
            'Where is that pit boss?',
        ])
        self.assertEqual([Action], [type(p) for p in paras])

    def test_simple_parenthetical(self):
        paras = parse([
            'STEEL',
            '(starting the engine)',
            'So much for retirement!',
        ])
        self.assertEqual(1, len(paras))
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
        paras = parse([
            'SOMEONE',
            'One',
            '  ',
            'Two',
        ])
        self.assertEqual([Dialog], [type(p) for p in paras])
        self.assertEqual([
            (False, plain('One')),
            (False, empty_string),
            (False, plain('Two')),
        ], paras[0].blocks)

    def test_dual_dialog(self):
        paras = parse([
            'BRICK',
            'Fuck retirement.',
            '',
            'STEEL ^',
            'Fuck retirement!',
        ])
        self.assertEqual([DualDialog], [type(p) for p in paras])
        dual = paras[0]
        self.assertEqual(plain('BRICK'), dual.left.character)
        self.assertEqual(
            [(False, plain('Fuck retirement.'))],
            dual.left.blocks
        )
        self.assertEqual(plain('STEEL'), dual.right.character)
        self.assertEqual(
            [(False, plain('Fuck retirement!'))],
            dual.right.blocks
        )

    def test_dual_dialog_without_previous_dialog_is_ignored(self):
        paras = parse([
            'Brick strolls down the street.',
            '',
            'BRICK ^',
            'Nice retirement.',
        ])
        self.assertEqual([Action, Dialog], [type(p) for p in paras])
        dialog = paras[1]
        self.assertEqual(plain('BRICK ^'), dialog.character)
        self.assertEqual([
            (False, plain('Nice retirement.'))
        ], dialog.blocks)

    def test_leading_and_trailing_spaces_in_dialog(self):
        paras = parse([
            'JULIET',
            'O Romeo, Romeo! wherefore art thou Romeo?',
            '  Deny thy father and refuse thy name;  ',
            'Or, if thou wilt not, be but sworn my love,',
            " And I'll no longer be a Capulet.",
        ])
        self.assertEqual([Dialog], [type(p) for p in paras])
        self.assertEqual([
            (False, plain('O Romeo, Romeo! wherefore art thou Romeo?')),
            (False, plain('Deny thy father and refuse thy name;')),
            (False, plain('Or, if thou wilt not, be but sworn my love,')),
            (False, plain("And I'll no longer be a Capulet.")),
        ], paras[0].blocks)


class TransitionTests(TestCase):

    def test_standard_transition(self):
        paras = parse([
            'Jack begins to argue vociferously in Vietnamese (?)',
            '',
            'CUT TO:',
            '',
            "EXT. BRICK'S POOL - DAY",
        ])
        self.assertEqual([Action, Transition, Slug], [type(p) for p in paras])

    def test_transition_must_end_with_to(self):
        paras = parse([
            'CUT TOO:',
            '',
            "EXT. BRICK'S POOL - DAY",
        ])
        self.assertEqual([Action, Slug], [type(p) for p in paras])

    def test_transition_needs_to_be_upper_case(self):
        paras = parse([
            'Jack begins to argue vociferously in Vietnamese (?)',
            '',
            'cut to:',
            '',
            "EXT. BRICK'S POOL - DAY",
        ])
        self.assertEqual([Action, Action, Slug], [type(p) for p in paras])

    def test_not_a_transition_on_trailing_whitespace(self):
        paras = parse([
            'Jack begins to argue vociferously in Vietnamese (?)',
            '',
            'CUT TO: ',
            '',
            "EXT. BRICK'S POOL - DAY",
        ])
        self.assertEqual([Action, Action, Slug], [type(p) for p in paras])

    def test_transition_does_not_have_to_be_followed_by_slug(self):
        # The "followed by slug" requirement is gone from the Jan 2012 spec
        paras = parse([
            'Bill lights a cigarette.',
            '',
            'CUT TO:',
            '',
            'SOME GUY mowing the lawn.',
        ])
        self.assertEqual(
            [Action, Transition, Action],
            [type(p) for p in paras]
        )

    def test_greater_than_sign_means_transition(self):
        paras = parse([
            'Bill blows out the match.',
            '',
            '> FADE OUT.',
            '',
            '.DARKNESS',
        ])
        self.assertEqual([Action, Transition, Slug], [type(p) for p in paras])
        self.assertEqual(plain('FADE OUT.'), paras[1].line)

    def test_centered_text_is_not_parsed_as_transition(self):
        paras = parse([
            'Bill blows out the match.',
            '',
            '> THE END. <',
            '',
            'bye!'
        ])
        self.assertEqual([Action, Action, Action], [type(p) for p in paras])

    def test_transition_at_end(self):
        paras = parse([
            'They stroll hand in hand down the street.',
            '',
            '> FADE OUT.',
        ])
        self.assertEqual([Action, Transition], [type(p) for p in paras])
        self.assertEqual(plain('FADE OUT.'), paras[1].line)


class ActionTests(TestCase):

    def test_action_preserves_leading_whitespace(self):
        paras = parse([
            'hello',
            '',
            '  two spaces',
            '   three spaces ',
        ])
        self.assertEqual([Action, Action], [type(p) for p in paras])
        self.assertEqual(
            [
                plain('  two spaces'),
                plain('   three spaces'),
            ], paras[1].lines
        )

    def test_single_centered_line(self):
        paras = parse(['> center me! <'])
        self.assertEqual([Action], [type(p) for p in paras])
        self.assertTrue(paras[0].centered)

    def test_full_centered_paragraph(self):
        lines = [
            '> first! <',
            '  > second!   <',
            '> third!< ',
        ]
        paras = parse(lines)
        self.assertEqual([Action], [type(p) for p in paras])
        self.assertTrue(paras[0].centered)
        self.assertEqual([
            plain('first!'),
            plain('second!'),
            plain('third!'),
        ], paras[0].lines)

    def test_upper_case_centered_not_parsed_as_dialog(self):
        paras = parse([
            '> FIRST! <',
            '  > SECOND! <',
            '> THIRD! <',
        ])
        self.assertEqual([Action], [type(p) for p in paras])
        self.assertTrue(paras[0].centered)

    def test_centering_marks_in_middle_of_paragraphs_are_verbatim(self):
        lines = [
            'first!',
            '> second! <',
            'third!',
        ]
        paras = parse(lines)
        self.assertEqual([Action], [type(p) for p in paras])
        self.assertFalse(paras[0].centered)
        self.assertEqual([plain(line) for line in lines], paras[0].lines)


class SynopsisTests(TestCase):
    def test_synopsis_after_slug_adds_synopsis_to_scene(self):
        paras = parse([
            "EXT. BRICK'S PATIO - DAY",
            '',
            "= Set up Brick & Steel's new life."
            '',
        ])
        self.assertEqual([Slug], [type(p) for p in paras])
        self.assertEqual(
            "Set up Brick & Steel's new life.",
            paras[0].synopsis
        )

    def test_synopsis_in_section(self):
        paras = parse([
            '# section one',
            '',
            '= In which we get to know our characters'
        ])
        self.assertEqual([Section], [type(p) for p in paras])
        self.assertEqual(
            'In which we get to know our characters',
            paras[0].synopsis
        )

    def test_synopsis_syntax_parsed_as_literal(self):
        paras = parse([
            'Some action',
            '',
            '= A line that just happens to look like a synopsis'
        ])
        self.assertEqual([Action, Action], [type(p) for p in paras])
        self.assertEqual(
            [plain('= A line that just happens to look like a synopsis')],
            paras[1].lines
        )


class TitlePageTests(TestCase):

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
            fountain.parse_title_page(lines)
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
            fountain.parse_title_page(lines)
        )

    def test_empty_value_ignored(self):
        lines = [
            'Title:',
            'Author: John August',
        ]
        self.assertDictEqual(
            {'Author': ['John August']},
            fountain.parse_title_page(lines)
        )

    def test_unparsable_title_page_returns_none(self):
        lines = [
            'Title: Inception',
            '    additional line',
        ]
        self.assertIsNone(fountain.parse_title_page(lines))


class PageBreakTests(TestCase):
    def test_page_break_is_parsed(self):
        paras = parse([
            '====',
            '',
            'So here we go'
        ])
        self.assertEqual([PageBreak, Action], [type(p) for p in paras])
