import re
import datetime
from . import template_to_regexp


class ReportParser:
    def parse(self, text):
        if not self._can_parse(text):
            raise ValueError(
                "Unable to parse reports with incomplete data."
                " See issue https://github.com/vitorbaptista/google-covid19-mobility-reports/issues/1."
            )

        country = self.parse_country(text)
        updated_at = self.parse_date(text)
        overall = self.parse_overall_mobility_changes(text)
        regions = self.parse_regions(text)

        country_and_regions = [overall] + regions
        for row in country_and_regions:
            row["country"] = country
            row["updated_at"] = updated_at

        return country_and_regions

    def parse_country(self, text):
        country, _ = self._parse_country_and_date(text)
        return country

    def parse_date(self, text):
        _, date = self._parse_country_and_date(text)
        return date

    def parse_overall_mobility_changes(self, text):
        template = """
We’ll leave a region out of the report if we don’t have statistically significant levels of data. To learn how
we calculate these trends and preserve privacy, read About this data.
Retail & recreation
+80%
{retail_and_recreation}%{IGNORE_LINES}
Grocery & pharmacy
+80%
{grocery_and_pharmacy}%{IGNORE_LINES}
Parks
+80%
{parks}%{IGNORE_LINES}
Transit stations
+80%
{transit_stations}%{IGNORE_LINES}
Workplaces
+80%
{workplaces}%{IGNORE_LINES}
Residential
+80%
{residential}%{IGNORE_LINES}
compared to baseline
        """.strip()

        data = _extract_groups_from_template(template, text)
        if not data:
            return

        parsed_data = {key: int(value) / 100 for (key, value) in data.items()}
        return parsed_data

    def parse_regions(self, text):
        regions = []

        text_subset = text
        region = self._parse_first_region(text_subset)

        while region:
            regions.append(region)
            next_subset_index = text_subset.find(region["region"]) + len(
                region["region"]
            )
            text_subset = text_subset[next_subset_index:]
            region = self._parse_first_region(text_subset)

        return regions

    def _parse_first_region(self, text):
        template = """
{region}
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
{workplaces}% compared to baseline
{residential}% compared to baseline
        """
        data = _extract_groups_from_template(template, text)
        if not data:
            return

        parsed_data = {
            key: int(value) / 100 for (key, value) in data.items() if key != "region"
        }
        parsed_data["region"] = data["region"].strip()
        return parsed_data

    def _parse_country_and_date(self, text):
        template = """
COVID-19 Community Mobility Report
{country_and_date}
Mobility changes
        """.strip()
        data = _extract_groups_from_template(template, text)
        if not data:
            return

        data_parts = data["country_and_date"].split(" ")
        country = " ".join(data_parts[:-3]).strip()
        date_str = " ".join(data_parts[-3:]).strip()

        date = datetime.datetime.strptime(date_str, "%B %d, %Y").date().isoformat()

        return country, date

    def _can_parse(self, text):
        return "Not enough data" not in text


def _extract_groups_from_template(template, text):
    regexp = template_to_regexp(template.strip())
    clean_text = re.sub("\\n\\n+", "\n", text.strip())
    clean_text = re.sub("  +", " ", clean_text)
    match = re.search(regexp, clean_text, re.MULTILINE)
    if match:
        return match.groupdict()
