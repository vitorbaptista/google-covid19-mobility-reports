import re
import datetime
from . import template_to_regexp


class ReportParser:
    def parse(self, text):
        return {
            'country': self.parse_country(text),
            'date': self.parse_date(text),
            'mobility_changes': self.parse_overall_mobility_changes(text),
            'regions': self.parse_regions(text),
        }

    def parse_country(self, text):
        country, _ = self._parse_country_and_date(text)
        return country

    def parse_date(self, text):
        _, date = self._parse_country_and_date(text)
        return date

    def parse_overall_mobility_changes(self, text):
        template = '''
We’ll leave a region out of the report if we don’t have statistically significant levels of data. To learn how
we calculate these trends and preserve privacy, read About this data.
Retail & recreation
+80%
{retail_and_recreation}%
compared to baseline
{IGNORE_LINES}
Grocery & pharmacy
+80%
{grocery_and_pharmacy}%
compared to baseline
{IGNORE_LINES}
Parks
+80%
{parks}%
compared to baseline
{IGNORE_LINES}
Transit stations
+80%
{transit_stations}%
compared to baseline
{IGNORE_LINES}
Workplaces
+80%
{workplaces}%
compared to baseline
{IGNORE_LINES}
Residential
+80%
{residential}%
compared to baseline
        '''.strip()

        data = _extract_groups_from_template(template, text)
        if not data:
            return

        parsed_data = {
            key: int(value) / 100
            for (key, value) in data.items()
        }
        return parsed_data

    def parse_regions(self, text):
        regions = []

        text_subset = text
        region = self._parse_first_region(text_subset)

        while region:
            regions.append(region)
            next_subset_index = text_subset.find(region['name']) + len(region['name'])
            text_subset = text_subset[next_subset_index:]
            region = self._parse_first_region(text_subset)

        return regions

    def _parse_first_region(self, text):
        template = '''
{name}
Retail & recreation
Grocery & pharmacy
Parks
{retail_and_recreation}% compared to baseline
{grocery_and_pharmacy}% compared to baseline
{parks}% compared to baseline
{IGNORE_LINES}
Transit stations
Workplace
Residential
{transit_stations}% compared to baseline
{workplace}% compared to baseline
{residential}% compared to baseline
        '''
        data = _extract_groups_from_template(template, text)
        if not data:
            return

        parsed_data = {
            key: int(value) / 100
            for (key, value) in data.items()
            if key != 'name'
        }
        parsed_data['name'] = data['name'].strip()
        return parsed_data

    def _parse_country_and_date(self, text):
        template = '''
COVID-19 Community Mobility Report
{country_and_date}
Mobility changes
        '''.strip()
        data = _extract_groups_from_template(template, text)
        if not data:
            return

        data_parts = data['country_and_date'].split(' ')
        country = ' '.join(data_parts[:-3])
        date_str = ' '.join(data_parts[-3:])

        date = datetime.datetime.strptime(date_str, '%B %d, %Y').date()
        
        return country, date


def _extract_groups_from_template(template, text):
    regexp = template_to_regexp(template.strip())
    clean_text = re.sub('\\n\\n+', '\n', text.strip())
    match = re.search(regexp, clean_text, re.MULTILINE)
    if match:
        return match.groupdict()