"""monitor log events"""


import dataclasses
import sqlite3
from typing import Optional

import alerts
import event
import notice
import statistics


@dataclasses.dataclass
class AlertState:
    name: str
    alert: alerts.Alert
    triggered: bool


@dataclasses.dataclass
class StatisticState:
    statistic: statistics.Statistic
    last_run_unix_time: Optional[int]


class Monitor:
    def __init__(self, alerts, statistics, on_notice):
        self.alerts = [AlertState(name, alert, triggered=False) for name, alert in alerts.items()]
        self.statistics = [StatisticState(statistic, last_run_unix_time=None) for statistic in statistics.values()]
        self.on_notice = on_notice
        self.db = setup_database()
        # Keep enough events (a window) to satisfy the alert/statistic having the widest window.
        self.window_seconds = max([
            *(state.alert.window_seconds() for state in self.alerts),
            *(state.statistic.period_seconds() for state in self.statistics)])

    def handle_event(self, ev: event.Event):
        db = self.db
        insert_event(db, ev)
        delete_old_events(db, self.window_seconds)
        oldest, newest = min_max_unix_times(db)
        horizon_seconds = newest - oldest

        for state in self.alerts:
            alert = state.alert
            if alert.window_seconds() > horizon_seconds:
                continue
            
            rows = list(db.execute(alert.sql_query()))
            status = alert.handle_query_result(rows)
            if status.triggered != state.triggered:
                state.triggered = status.triggered
                self.on_notice(notice.Alert(
                        unix_time=ev.unix_time,
                        name=state.name,
                        is_triggered=state.triggered,
                        message=status.message))

        for state in self.statistics:
            period = state.statistic.period_seconds()
            if period > horizon_seconds:
                continue
            last_run = state.last_run_unix_time
            if last_run is not None and newest - last_run < period:
                continue

            state.last_run_unix_time = newest
            self.on_notice(notice.Table(
                    unix_time=ev.unix_time,
                    title=f'{state.statistic.title()} (last {period} seconds)',
                    column_names=state.statistic.column_names(),
                    rows=list(db.execute(state.statistic.sql_query()))))


def setup_database():
    db = sqlite3.connect(':memory:')
    columns = ', '.join(event.field_names())
    db.execute(f"create table Events({columns});")
    db.execute(f"create index Index_Events_unix_time on Events(unix_time);")
    # Note: As the number of events "in window" becomes large, it may become
    # advantageous to add indices on other columns, depending on the queries
    # performed by statistics and alerts.
    return db


def insert_event(db, ev: event.Event):
    columns = ', '.join(event.field_names())
    placeholders = ', '.join(('?' for _ in event.field_names()))
    values = dataclasses.astuple(ev)
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
            (select max(unix_time) from Events
            where unix_time <= (select max(unix_time) from Events) - ?);""",
        (window_seconds,))


def min_max_unix_times(db):
    (oldest, newest), = db.execute("""
        select min(unix_time), max(unix_time) from Events;
    """)
    return oldest, newest
