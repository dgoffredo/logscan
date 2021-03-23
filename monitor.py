"""monitor log events"""


import alerts
import event
import statistics
import dataclasses
import sqlite3
from typing import Optional


@dataclasses.dataclass
class AlertState:
    name: str
    alert: alerts.Alert
    triggered: bool


@dataclasses.dataclass
class StatisticState:
    name: str
    statistic: statistics.Statistic
    last_run_unix_time: Optional[int]


class Monitor:
    def __init__(self, alerts, statistics, on_notice):
        self.alerts = [AlertState(name, alert, triggered=False) for name, alert in alerts.items()]
        self.statistics = [StatisticState(name, statistic, last_run_unix_time=None) for name, statistic in statistics.items()]
        self.on_notice = on_notice
        self.db = setup_database()
        # Keep enough events (a window) to satisfy the alert/statistic having the widest window.
        self.window_seconds = max(
            *(state.alert.window_seconds() for state in self.alerts),
            *(state.statistic.period_seconds() for state in self.statistics))

    def handle_event(self, event: event.Event):
        insert_event(self.db, event)

        for state in self.alerts:
            pass # TODO

        for state in self.statistics:
            pass # TODO

        delete_old_events(self.db, self.window_seconds)


def setup_database():
    db = sqlite3.connect(':memory:')
    columns = ', '.join(event.field_names())
    db.execute(f"create table Events({columns});")
    db.execute(f"create index Index_Events_unix_time on Events(unix_time)")
    return db


def insert_event(db, event: event.Event):
    columns = ', '.join(event.field_names())
    placeholders = ', '.join(('?' for _ in columns))
    values = dataclasses.astuple(event)
    db.execute(f"insert into Events({columns}) values ({placeholders});", values)


def delete_old_events(db, window_seconds: float):
    # Say we're looking 10 seconds behind, and the timestamps look like this:
    #
    #     ..., 4, 4, 5, 6, 6, 8, 8, 8, 9, 12, 15, 16, 16, 17
    #
    # 17 - 10 is 7, so we keep 6 and greater.  If there were an event with
    # timestamp 7, then we'd delete the events with timestamp 6.
    db.execute("""
        delete from Events where unix_time <
            (select max(unix_time)
            where unix_time <= (select max(unix_time)) - ?);""",
        window_seconds)
