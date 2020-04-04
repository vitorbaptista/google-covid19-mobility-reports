import argparse
import sys
import csv
from pdfminer.high_level import extract_text
from mobility_reports import ReportParser


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert Google COVID-19 mobility reports to JSON."
    )
    parser.add_argument(
        "report_file",
        type=argparse.FileType("rb"),
        default=sys.stdin,
        help="Google COVID-19 mobility report PDF file",
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
    text = extract_text(args.report_file)
    parser = ReportParser()
    data = parser.parse(text)

    write_as_csv(data, sys.stdout)


if __name__ == "__main__":
    main()
