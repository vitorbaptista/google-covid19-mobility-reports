import re
import pytest

from mobility_reports import template_to_regexp


class TestTemplateToRegexp:
    def test_converts_template_to_groups(self):
        template = 'I want {what_do_i_want}.'
        text = 'I want to break free.'
        regexp = template_to_regexp(template)
        matches = re.match(regexp, text)

        assert matches.groupdict() == {
            'what_do_i_want': 'to break free',
        }

    @pytest.mark.parametrize('text,number', (
        ('''
Hello.
I want some things.
Is there anybody out there.
        '''.strip(), 'some'),
        ('''
Hello.
I want many things.
Is there anybody out there.
        '''.strip(), 'many'),
    ))
    def test_ignores_ignore_tags(self, text, number):
        template = '''
{IGNORE}
I want {number} things.
{IGNORE}
        '''.strip()
        regexp = template_to_regexp(template)
        matches = re.match(regexp, text)
        assert matches.groupdict() == {
            'number': number,
        }

    def test_ignore_multilines(self):
        """Ignore multilines is non-greedy."""
        text = '''
Hello.
I have another line.
And another one.
How are you?
How are me?
        '''
        template = '''
Hello.
{IGNORE_LINES}
How are {who}?
'''
        regexp = template_to_regexp(template)
        matches = re.search(regexp, text, re.MULTILINE)
        assert matches.groupdict() == {
            'who': 'you',
        }
