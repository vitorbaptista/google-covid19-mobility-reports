import argparse
import sys
import json
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


def main():
    args = parse_args()
    text = extract_text(args.report_file)
    parser = ReportParser()
    data = parser.parse(text)
    print(json.dumps(data))


if __name__ == "__main__":
    main()
