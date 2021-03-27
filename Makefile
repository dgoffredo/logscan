logscan: $(shell git ls-files)
	bin/distribute $@

.PHONY: test
test:
	python3 -m unittest
