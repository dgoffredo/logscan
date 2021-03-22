"""monitor log events"""


import alerts
import statistics
import dataclasses
import sqlite3
from typing import Optional


@dataclasses.dataclass
class AlertState:
    triggered: bool
    alert: alerts.Alert


@dataclasses.dataclass
class StatisticState:
    last_run_unix_time: Optional[int]
    statistic: statistics.Statistic


class Monitor:
    def __init__(self, alerts, statistics, on_notice):
        self.alerts = [AlertState(triggered=False, alert=alert) for alert in alerts]
        self.statistics = [StatisticState(last_run_unix_time=None, statistic=stat) for stat in statistics]
        self.on_notice = on_notice
        self.db = setup_database()

    def handle_event(self, event):
        pass # TODO


def setup_database():
    db = sqlite3.connect(':memory:')
    db.execute(f"create table Events({', '.join(event.field_names())});")
    db.commit()
    return db
