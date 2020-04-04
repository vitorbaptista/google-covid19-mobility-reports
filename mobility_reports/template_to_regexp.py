import re


def template_to_regexp(template):
    ignore_regexp = r'\\{IGNORE\\}'
    groups_regexp = r'\\{([^}]+)\\}'
    escaped_template = re.escape(template)
    converted = re.sub(ignore_regexp, '.+', escaped_template)
    converted = re.sub(groups_regexp, '(?P<\\1>.+)', converted)

    return converted