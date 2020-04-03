PHONY := data reports
DATE := $(shell date --utc --iso-8601)
REPORTS_DIR := data/raw/reports

data: Makefile.reports.mk
	make --jobs=8 reports

data/processed/reports_urls.txt: data/raw/html/$(DATE).html
	grep -oE 'http.*gstatic.*pdf' $< >> $@
	sort $@ -o $@

data/raw/html/$(DATE).html:
	curl https://www.google.com/covid19/mobility/ -Lo $@

Makefile.reports.mk: data/processed/reports_urls.txt
	@cat $< | while read f; do echo "$(REPORTS_DIR)/$${f##*/}:\n\tcurl $$f -sLo \$$@"; done > $@
	@echo "reports: " $(shell sed -e 's/.*\/\(.*\)/data\/raw\/reports\/\1/g' $< | sed ':a;/./{N;s/\n/ /;ba}' -) >> $@

-include Makefile.reports.mk
