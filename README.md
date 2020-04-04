# Google COVID-19 Mobility Reports

Archive of the [Google COVID-19 Mobility Reports'][google-reports] PDFs and their data extracted
as a CSV.

## Motivation

Google launched [a series of reports][google-reports] on their user's mobility
during the Coronavirus pandemic. According to their website, the reports "chart
movement trends over time by geography, across different categories of places
such as retail and recreation, groceries and pharmacies, parks, transit
stations, workplaces, and residential."

![report-screenshot.png](https://www.google.com/covid19/mobility/static/image.png "Louisiana's Community Mobility Report shows a 45% decrease in visits to places like restaurants and shopping centers and a 16% decrease in visits to places like groceries and pharmacies since January.")

This data is very interesting and important during these times. However, it's
only available as a PDF per country (or per State in the USA). This project has
two goals:

1. Provide an archive of the reports
2. Extract this data into a more convenient format (CSV or JSON)

## Where is the data?

* Raw PDF reports: [data/raw/reports](data/raw/reports)
* Reports converted to CSV: [data/processed/reports](data/processed/reports)
  * Not all reports were converted to CSVs yet

[google-reports]: https://www.google.com/covid19/mobility/
This repository contains a copy of all 
