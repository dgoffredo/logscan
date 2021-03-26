"""routines for notices

A notice is emitted by the log monitor to indicate something of interest,
e.g. a periodic metrics summary or a triggered alert condition.

Notices have two output formats: JSON and pretty.  JSON is intended for
programmatic consumption, while pretty is intended for human eyeballs.
"""


import dataclasses
import json
from typing import List
from tabulate import tabulate


@dataclasses.dataclass
class Alert:
    unix_time: int
    name: str
    is_triggered: bool
    message: str

    def to_pretty(self):
        buzzword = 'TRIGGERED' if self.is_triggered else 'RECOVERED'
        return f'@{self.unix_time} ALERT {self.name} {buzzword}: {self.message}'

    def to_json(self):
        return to_json(self)


@dataclasses.dataclass
class Table:
    unix_time: int
    title: str
    column_names: List[str]
    rows: List[tuple]

    def to_pretty(self):
        return f'@{self.unix_time}\n{self.title}\n' + tabulate(self.rows, self.column_names, tablefmt="fancy_grid")

    def to_json(self):
        return to_json(self)


def to_json(notice):
    # e.g. {"unix_time": 12345678 ,"Alert": {"name": "foo", "is_triggered": true, "message": "AHH"}}
    return json.dumps({
        'unix_time': notice.unix_time,
        type(notice).__name__: {
            name: value for name, value in dataclasses.asdict(notice).items() \
            if name != 'unix_time'
        }
    })
