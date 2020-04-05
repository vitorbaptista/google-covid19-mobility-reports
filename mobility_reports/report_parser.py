import re
import math
import datetime
from . import template_to_regexp


class ReportParser:
    def parse(self, text):
        region = self.parse_region(text)
        updated_at = self.parse_date(text)
        overall = self.parse_overall_mobility_changes(text)
        subregions = self.parse_subregions(text)

        region_and_subregions = [overall] + subregions
        for row in region_and_subregions:
            row["region"] = region
            row["updated_at"] = updated_at

        return region_and_subregions

    def parse_region(self, text):
        region, _ = self._parse_region_and_date(text)
        return region

    def parse_date(self, text):
        _, date = self._parse_region_and_date(text)
        return date

    def parse_overall_mobility_changes(self, text):
        keys = [
            "retail_and_recreation",
            "grocery_and_pharmacy",
            "parks",
            "transit_stations",
            "workplaces",
            "residential",
        ]
        subset_index = text.find("Mobility trends for places of residence")
        subset_index = text.find("\x0c", subset_index)
        region_report_pages = text[:subset_index]
        values = re.findall(r"^(\S+)%", region_report_pages, re.MULTILINE)

        data = {key: int(value) / 100 for (key, value) in zip(keys, values)}
        return data

    def parse_subregions(self, text):
        subregions = []

        # Skip first pages that don't have region data.
        index = text.find("Mobility trends for places of residence")
        if index != -1:
            text_subset = text[index:]
        else:
            text_subset = text

        subregion = self._parse_first_subregion(text_subset)

        while subregion:
            subregions.append(subregion)
            next_subset_index = text_subset.find(subregion["subregion"]) + len(
                subregion["subregion"]
            )
            text_subset = text_subset[next_subset_index:]
            subregion = self._parse_first_subregion(text_subset)

        return subregions

    def _parse_first_subregion(self, text):
        regexp = r"""
(?P<subregion>[^\*\n]+)[\n]*?
Retail \& recreation
        """.strip()
        data = _extract_groups_from_regexp(regexp, text)
        if not data:
            return

        index = text.find(data["subregion"])
        if index == -1:
            raise ValueError("Could not parse")

        text_subset = text[index:]
        data["subregion"] = data["subregion"].strip()
        data.update(self._extract_subregion_values(text_subset))
        not_enough = self._extract_subregion_not_enough_data_markers(text_subset)

        for not_enough_column in not_enough:
            data[f"{not_enough_column}_not_enough_data"] = True

        return data

    def _extract_subregion_values(self, text):
        keys = [
            "retail_and_recreation",
            "grocery_and_pharmacy",
            "parks",
            "transit_stations",
            "workplaces",
            "residential",
        ]
        data_regexp = r"""((?P<data>-?\d+)% compared to baseline|Not enough data for this date[^:])"""

        text_subset = text
        data = {}
        for key in keys:
            match = re.search(data_regexp, text_subset)
            value = None
            if match:
                text_subset = text_subset[match.end() :]

                try:
                    value = match.groupdict()["data"]
                    value = int(value) / 100
                except:
                    pass

            data[key] = value

        return data

    def _extract_subregion_not_enough_data_markers(self, text):
        """Returns the columns with not enough data indicators.

        These columns are marked with an asterisk. As the text extracted from
        the PDFs isn't very reliable, the algorithm is:

        1. Look for the column names and save their (x, y) positions i.e. (column, row)
        2. Look for the asterisks and save their (x, y) positions
        3. Filter the asterisks that are too far away from the column names
          This avoids considering asterisks in the footer of the page or other pages.
        4. Use Euclidian distance to match the asterisk closest to the column names
        5. Return the list of columns with a nearby asterisk
        """
        columns = {
            "retail_and_recreation": "Retail & recreation",
            "grocery_and_pharmacy": "Grocery & pharmacy",
            "parks": "Parks",
            "transit_stations": "Transit stations",
            "workplaces": "Workplace",
            "residential": "Residential",
        }
        columns_positions = {}
        max_line_length = -1

        # Only consider text in a single page
        next_page_break = text[5:].find("\x0c")
        if next_page_break != -1:
            text_subset = text[:next_page_break]

        for (y, row) in enumerate(text_subset.splitlines()):
            if len(row) > max_line_length:
                max_line_length = len(row)
            for (key, column) in columns.items():
                x = row.find(column)
                if x != -1:
                    columns_positions[key] = (x + len(column) // 2, y)
            if len(columns_positions) == len(columns):
                break

        asterisks_positions = []
        for (y, row) in enumerate(text_subset.splitlines()):
            x = row.find("*")
            while x != -1:
                asterisks_positions.append((x, y))
                row = row[x + 1 :]
                x = row.find("*")

        # Filter only asterisks that are near our columns to avoid
        # using other asterisks on the page.
        min_y = min([y for (key, (x, y)) in columns_positions.items()])
        max_y = max([y for (key, (x, y)) in columns_positions.items()]) + 5
        asterisks_candidates = [
            (x, y) for (x, y) in asterisks_positions if y >= min_y and y <= max_y
        ]

        not_enough_data = set()
        for (asterisk_x, asterisk_y) in asterisks_candidates:
            if asterisk_y < min_y or asterisk_y > max_y:
                # Avoid parsing asterisks not related to this region
                continue
            nearest_column_distance = float("inf")
            nearest_column = None
            for (col, (col_x, col_y)) in columns_positions.items():
                if col in not_enough_data:
                    continue

                distance = math.sqrt(
                    (asterisk_x - col_x) ** 2 + (asterisk_y - col_y) ** 2
                )
                if distance < nearest_column_distance:
                    nearest_column_distance = distance
                    nearest_column = col
            if nearest_column:
                not_enough_data.add(nearest_column)

        return not_enough_data

    def _parse_region_and_date(self, text):
        template = """
COVID-19 Community Mobility Report
{region_and_date}
Mobility changes
        """.strip()
        data = _extract_groups_from_template(template, text)
        if not data:
            return

        data_parts = data["region_and_date"].split(" ")
        region = " ".join(data_parts[:-3]).strip()
        date_str = " ".join(data_parts[-3:]).strip()

        date = datetime.datetime.strptime(date_str, "%B %d, %Y").date().isoformat()

        return region, date


def _extract_groups_from_template(template, text):
    regexp = template_to_regexp(template.strip())
    clean_text = re.sub("\\n\\n+", "\n", text.strip())
    clean_text = re.sub("  +", " ", clean_text)
    match = re.search(regexp, clean_text)
    if match:
        return match.groupdict()


def _extract_groups_from_regexp(regexp, text):
    clean_text = re.sub("\\n\\n+", "\n", text.strip())
    clean_text = re.sub("  +", " ", clean_text)
    match = re.search(regexp, clean_text)
    if match:
        return match.groupdict()
