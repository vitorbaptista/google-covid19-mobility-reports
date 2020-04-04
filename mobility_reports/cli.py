import argparse
import sys
import csv
import subprocess
from mobility_reports import ReportParser


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert Google COVID-19 mobility reports to JSON."
    )
    parser.add_argument(
        "report_path", help="Google COVID-19 mobility report PDF file path",
    )

    return parser.parse_args()


def write_as_csv(data, output):
    fieldnames = [
        "country",
        "region",
        "updated_at",
        "retail_and_recreation",
        "grocery_and_pharmacy",
        "parks",
        "transit_stations",
        "workplaces",
        "residential",
    ]
    csvwriter = csv.DictWriter(output, fieldnames=fieldnames)
    csvwriter.writeheader()

    csvwriter.writerows(data)


def main():
    args = parse_args()
    text = subprocess.check_output(
        ["pdftotext", args.report_path, "-"], universal_newlines=True
    )
    parser = ReportParser()
    data = parser.parse(text)

    write_as_csv(data, sys.stdout)


if __name__ == "__main__":
    main()
