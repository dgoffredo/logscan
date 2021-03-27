logscan: $(shell git ls-files)
	bin/distribute $@

.PHONY: test
test:
	python3 -m unittest

.PHONY: profile
profile:
	python3 -m cProfile -o profile.out __main__.py data/access.log >/dev/null
	bin/visualize-profile profile.out
