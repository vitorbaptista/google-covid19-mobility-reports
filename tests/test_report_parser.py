import os
import pathlib
import re
import pytest
from mobility_reports import ReportParser


class TestReportParser:
    def test_parse(self, br_fixture):
        parser = ReportParser()
        data = parser.parse(br_fixture)
        assert data["country"] == "Brazil"
        assert data["date"] == "2020-03-29"
        assert data["mobility_changes"]["parks"] == -0.7  # Try a sample
        assert len(data["regions"]) == 27

    def test_parse_country(self, br_fixture):
        report = ReportParser()
        assert report.parse_country(br_fixture) == "Brazil"

    def test_parse_country_gb(self, gb_fixture):
        report = ReportParser()
        assert report.parse_country(gb_fixture) == "United Kingdom"

    def test_parse_date(self, br_fixture):
        report = ReportParser()
        assert report.parse_date(br_fixture) == "2020-03-29"

    def test_parse_overall_mobility_changes_br(self, br_fixture):
        expected_data = {
            "retail_and_recreation": -0.71,
            "grocery_and_pharmacy": -0.35,
            "parks": -0.7,
            "transit_stations": -0.62,
            "workplaces": -0.34,
            "residential": 0.17,
        }
        parser = ReportParser()
        data = parser.parse_overall_mobility_changes(br_fixture)
        assert data == expected_data

    def test_parse_overall_mobility_changes_gb(self, gb_fixture):
        expected_data = {
            "retail_and_recreation": -0.85,
            "grocery_and_pharmacy": -0.46,
            "parks": -0.52,
            "transit_stations": -0.75,
            "workplaces": -0.55,
            "residential": 0.15,
        }
        parser = ReportParser()
        data = parser.parse_overall_mobility_changes(gb_fixture)
        assert data == expected_data

    def test_parse_regions(self, br_fixture):
        expected_data = [
            {
                "retail_and_recreation": -0.68,
                "grocery_and_pharmacy": -0.28,
                "parks": -0.63,
                "transit_stations": -0.56,
                "workplace": -0.36,
                "residential": 0.2,
                "name": "Federal District",
            },
            {
                "retail_and_recreation": -0.68,
                "grocery_and_pharmacy": -0.2,
                "parks": -0.56,
                "transit_stations": -0.75,
                "workplace": -0.22,
                "residential": 0.11,
                "name": "State of Acre",
            },
            {
                "retail_and_recreation": -0.77,
                "grocery_and_pharmacy": -0.43,
                "parks": -0.79,
                "transit_stations": -0.76,
                "workplace": -0.35,
                "residential": 0.17,
                "name": "State of Alagoas",
            },
            {
                "retail_and_recreation": -0.71,
                "grocery_and_pharmacy": -0.27,
                "parks": -0.51,
                "transit_stations": -0.73,
                "workplace": -0.28,
                "residential": 0.11,
                "name": "State of Amapá",
            },
            {
                "retail_and_recreation": -0.64,
                "grocery_and_pharmacy": -0.28,
                "parks": -0.62,
                "transit_stations": -0.46,
                "workplace": -0.26,
                "residential": 0.13,
                "name": "State of Amazonas",
            },
            {
                "retail_and_recreation": -0.73,
                "grocery_and_pharmacy": -0.42,
                "parks": -0.71,
                "transit_stations": -0.73,
                "workplace": -0.33,
                "residential": 0.17,
                "name": "State of Bahia",
            },
            {
                "retail_and_recreation": -0.76,
                "grocery_and_pharmacy": -0.34,
                "parks": -0.71,
                "transit_stations": -0.68,
                "workplace": -0.33,
                "residential": 0.16,
                "name": "State of Ceará",
            },
            {
                "retail_and_recreation": -0.68,
                "grocery_and_pharmacy": -0.35,
                "parks": -0.69,
                "transit_stations": -0.69,
                "workplace": -0.31,
                "residential": 0.16,
                "name": "State of Espírito Santo",
            },
            {
                "retail_and_recreation": -0.67,
                "grocery_and_pharmacy": -0.27,
                "parks": -0.44,
                "transit_stations": -0.5,
                "workplace": -0.28,
                "residential": 0.15,
                "name": "State of Goiás",
            },
            {
                "retail_and_recreation": -0.63,
                "grocery_and_pharmacy": -0.27,
                "parks": -0.48,
                "transit_stations": -0.66,
                "workplace": -0.2,
                "residential": 0.11,
                "name": "State of Maranhão",
            },
            {
                "retail_and_recreation": -0.63,
                "grocery_and_pharmacy": -0.3,
                "parks": -0.44,
                "transit_stations": -0.59,
                "workplace": -0.22,
                "residential": 0.11,
                "name": "State of Mato Grosso",
            },
            {
                "retail_and_recreation": -0.68,
                "grocery_and_pharmacy": -0.33,
                "parks": -0.56,
                "transit_stations": -0.68,
                "workplace": -0.26,
                "residential": 0.14,
                "name": "State of Mato Grosso do Sul",
            },
            {
                "retail_and_recreation": -0.66,
                "grocery_and_pharmacy": -0.29,
                "parks": -0.46,
                "transit_stations": -0.57,
                "workplace": -0.3,
                "residential": 0.15,
                "name": "State of Minas Gerais",
            },
            {
                "retail_and_recreation": -0.75,
                "grocery_and_pharmacy": -0.42,
                "parks": -0.7,
                "transit_stations": -0.64,
                "workplace": -0.34,
                "residential": 0.17,
                "name": "State of Paraná",
            },
            {
                "retail_and_recreation": -0.76,
                "grocery_and_pharmacy": -0.36,
                "parks": -0.73,
                "transit_stations": -0.64,
                "workplace": -0.33,
                "residential": 0.17,
                "name": "State of Paraíba",
            },
            {
                "retail_and_recreation": -0.61,
                "grocery_and_pharmacy": -0.25,
                "parks": -0.53,
                "transit_stations": -0.64,
                "workplace": -0.19,
                "residential": 0.12,
                "name": "State of Pará",
            },
            {
                "retail_and_recreation": -0.74,
                "grocery_and_pharmacy": -0.35,
                "parks": -0.72,
                "transit_stations": -0.59,
                "workplace": -0.35,
                "residential": 0.17,
                "name": "State of Pernambuco",
            },
            {
                "retail_and_recreation": -0.71,
                "grocery_and_pharmacy": -0.39,
                "parks": -0.49,
                "transit_stations": -0.76,
                "workplace": -0.27,
                "residential": 0.18,
                "name": "State of Piauí",
            },
            {
                "retail_and_recreation": -0.74,
                "grocery_and_pharmacy": -0.36,
                "parks": -0.74,
                "transit_stations": -0.66,
                "workplace": -0.33,
                "residential": 0.19,
                "name": "State of Rio Grande do Norte",
            },
            {
                "retail_and_recreation": -0.75,
                "grocery_and_pharmacy": -0.39,
                "parks": -0.73,
                "transit_stations": -0.67,
                "workplace": -0.36,
                "residential": 0.2,
                "name": "State of Rio Grande do Sul",
            },
            {
                "retail_and_recreation": -0.72,
                "grocery_and_pharmacy": -0.32,
                "parks": -0.74,
                "transit_stations": -0.61,
                "workplace": -0.37,
                "residential": 0.17,
                "name": "State of Rio de Janeiro",
            },
            {
                "retail_and_recreation": -0.63,
                "grocery_and_pharmacy": -0.27,
                "parks": -0.42,
                "transit_stations": -0.71,
                "workplace": -0.23,
                "residential": 0.12,
                "name": "State of Rondônia",
            },
            {
                "retail_and_recreation": -0.68,
                "grocery_and_pharmacy": -0.25,
                "parks": -0.51,
                "transit_stations": -0.72,
                "workplace": -0.24,
                "residential": 0.12,
                "name": "State of Roraima",
            },
            {
                "retail_and_recreation": -0.8,
                "grocery_and_pharmacy": -0.49,
                "parks": -0.84,
                "transit_stations": -0.76,
                "workplace": -0.4,
                "residential": 0.2,
                "name": "State of Santa Catarina",
            },
            {
                "retail_and_recreation": -0.78,
                "grocery_and_pharmacy": -0.46,
                "parks": -0.77,
                "transit_stations": -0.83,
                "workplace": -0.36,
                "residential": 0.18,
                "name": "State of Sergipe",
            },
            {
                "retail_and_recreation": -0.72,
                "grocery_and_pharmacy": -0.36,
                "parks": -0.71,
                "transit_stations": -0.62,
                "workplace": -0.37,
                "residential": 0.17,
                "name": "State of São Paulo",
            },
            {
                "retail_and_recreation": -0.61,
                "grocery_and_pharmacy": -0.31,
                "parks": -0.35,
                "transit_stations": -0.71,
                "workplace": -0.19,
                "residential": 0.11,
                "name": "State of Tocantins",
            },
        ]
        parser = ReportParser()
        data = parser.parse_regions(br_fixture)

        assert data == expected_data

    @pytest.mark.skip(reason="cannot parse PDFs with regions without enough data yet")
    def test_parse_region_without_enough_data(self, gb_fixture):
        expected_data = {
            "name": "Blaenau Gwent",
            "retail_and_recreation": -0.75,
            "grocery_and_pharmacy": -0.46,
            "parks": None,
            "transit_stations": -0.57,
            "workplace": -0.46,
            "residential": 0.12,
            "retail_and_recreation_significant": True,
            "grocery_and_pharmacy_significant": True,
            "parks_significant": False,
            "transit_stations_significant": False,
            "workplace_significant": True,
            "residential_significant": False,
        }
        parser = ReportParser()
        regions = parser.parse_regions(gb_fixture)
        blaenau = [
            region for region in regions if region["name"] == expected_data["name"]
        ]
        assert len(blaenau) == 1
        blaenau = blaenau[0]

        assert blaenau == expected_data


@pytest.fixture(scope="session")
def br_fixture():
    path = (
        pathlib.Path(__file__).parent / "fixtures/2020-03-29_BR_Mobility_Report_en.txt"
    )
    with open(path, "rt") as fp:
        contents = fp.read()
    return contents


@pytest.fixture(scope="session")
def gb_fixture():
    path = (
        pathlib.Path(__file__).parent / "fixtures/2020-03-29_GB_Mobility_Report_en.txt"
    )
    with open(path, "rt") as fp:
        contents = fp.read()
    return contents
