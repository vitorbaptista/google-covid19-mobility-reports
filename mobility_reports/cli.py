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
        "report_paths", nargs="+", help="Google COVID-19 mobility report PDF file path",
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

    sorted_data = sorted(
        data, key=lambda row: (row["country"], row.get("region", ""), row["updated_at"])
    )
    csvwriter.writerows(sorted_data)


def main():
    args = parse_args()

    all_data = []
    for report_path in args.report_paths:
        text = subprocess.check_output(
            ["pdftotext", report_path, "-"], universal_newlines=True
        )
        parser = ReportParser()
        try:
            data = parser.parse(text)
        except ValueError:
            # Ignore value errors, raised when the file is unparseable.
            continue
        except Exception as e:
            raise ValueError(f"Could not parse report {report_path}") from e
        if data:
            all_data += data

    write_as_csv(all_data, sys.stdout)


if __name__ == "__main__":
    main()
