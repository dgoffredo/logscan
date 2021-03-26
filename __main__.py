# TODO (use command line interface)

import csv
import sys

import alerts
import event
import monitor
import statistics


def on_notice(notice):
    print(notice.to_pretty())
    print()


alert_objects = {}
for name, klass in alerts.alerts.items():
    if name == 'total_volume':
        alert_objects[name] = klass(volume_threshold_per_second=10)
    else:
        alert_objects[name] = klass()


statistics_objects = {name: klass() for name, klass in statistics.statistics.items()}


monitor = monitor.Monitor(alert_objects, statistics_objects, on_notice)
reader = csv.reader(sys.stdin)

next(reader)
for row in reader:
    remote_host, rfc931, authuser, unix_time, request, response_status, response_bytes = row
    ev = event.Event(remote_host, int(unix_time), request, int(response_status), int(response_bytes))
    monitor.handle_event(ev)
