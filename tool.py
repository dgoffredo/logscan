"""HTTP access log monitor command line tool"""

import argparse
import csv
import sys

import alerts
import event
import monitor
import statistics


def main():
    options = parse_command_line(sys.argv[1:])
    input_file = open_input_file(options)
    analyze_log(
        input_file_object=input_file,
        use_json=options.json,
        show_statistics=(not options.no_statistics),
        alert_volume_threshold_per_second=options.threshold)


def analyze_log(input_file_object, use_json, show_statistics, alert_volume_threshold_per_second):
    def on_notice(notice):
        if use_json:
            print(notice.to_json())
        else:
            print(notice.to_pretty())
            print()

    alert_objects = {}
    for name, klass in alerts.alerts.items():
        if name == 'total_volume':
            alert_objects[name] = klass(alert_volume_threshold_per_second)
        else:
            alert_objects[name] = klass()

    if show_statistics:
        statistics_objects = {
            name: klass() for name, klass in statistics.statistics.items()
        }
    else:
        statistics_objects = {}

    handle_event = monitor.Monitor(alert_objects, statistics_objects, on_notice).handle_event

    reader = csv.reader(input_file_object)
    # skip the first line (column names)
    if next(reader, None) is None:
        return

    for row in reader:
        remote_host, rfc931, authuser, unix_time, request, response_status, response_bytes = row
        ev = event.Event(remote_host, int(unix_time), request, int(response_status), int(response_bytes))
        handle_event(ev)


def parse_command_line(args):
    parser = argparse.ArgumentParser(description='Analyze an HTTP access log')

    parser.add_argument('log_file', nargs='?',
        help='HTTP access log file (standard input if "-" or omitted)')
    parser.add_argument('--no-statistics', dest='no_statistics', action='store_true', default=False,
        help="Don't print any statistics about the log")
    parser.add_argument('--json', action='store_true', default=False,
        help='Print output as JSON lines')
    parser.add_argument('--threshold', type=float, default=10,
        help='Alerting threshold in average requests per second')

    return parser.parse_args(args)

def open_input_file(options):
    if options.log_file is None or options.log_file == '-':
        return sys.stdin
    return open(options.log_file)
