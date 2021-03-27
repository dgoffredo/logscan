# logscan
Generate statistics and alert notifications from an HTTP access log.

## Why
This is a coding assignment for a job interview.

## What
`logscan` is a command line tool that takes a comma-separated-values HTTP
access log in a particular format, and prints to standard output periodic
statistics and alert notifications.

## How
```console
$ ./logscan --help
usage: logscan [-h] [--no-statistics] [--json] [--threshold THRESHOLD] [log_file]

Analyze an HTTP access log

positional arguments:
  log_file              HTTP access log file (standard input if "-" or omitted)

optional arguments:
  -h, --help            show this help message and exit
  --no-statistics       Don't print any statistics about the log
  --json                Print output as JSON lines
  --threshold THRESHOLD
                        Alerting threshold in average requests per second
```

See [data/access.log](data/access.log) for an example of a log in the expected
format.

## More

### Building
This git repository is an executable python package.  It may be invoked using a
python3 interpreter, e.g.:
```console
$ python3 ./ --help
```

There is also a `make` file target, `./logscan` that produces an executable
python3 zip archive of this repository, e.g.:
```console
$ make
bin/distribute logscan
$ ./logscan --help
```

### Testing
This repository contains `test_*.py` unit test files that can be discovered by
the python standard `unittest` module.  There is a `make` phony target, `test`,
that runs the tests, e.g.:
```console
$ make test
python3 -m unittest
....
----------------------------------------------------------------------
Ran 4 tests in 0.049s

OK
```

### Hacking
See the other `README.md` files within the respository.

- [statistics](statistics/README.md)
- [alerts](alerts/README.md)
- [data](data/README.md)

### Performance Profiling
There is a `make` phony target, `profile`, that using the python standard
`cProfile` module to instrument a run of logscan using the `data/access.log`
as input.  The binary-formatted result of the profile is written to
`profile.out`, and then `snakeviz` is used to generate a report and display it
in a web browser, e.g.:
```console
$ make profile
python3 -m cProfile -o profile.out __main__.py data/access.log >/dev/null
bin/visualize-profile profile.out
snakeviz web server started on 127.0.0.1:8080; enter Ctrl-C to exit
http://127.0.0.1:8080/snakeviz/%2Fhome%2Fdavid%2Fsrc%2Flogscan%2Fprofile.out
```

### Thoughts on the Design
See [NOTES.md](NOTES.md).
