# Alerts
An alert is SQL query that is evaluated each time an event is processed by
logscan.  The results of the query are passed to a handler function that then
returns whether the alert is "triggered" and additionally a message describing
the current state of the alert.

Each alert has a `window_seconds`: the number of seconds back in time from
the most recent event that the alert requires to be able to see.  The
horizon (oldest event) of the `Events` table in the sqlite database on which
the query is executed may be older than `window_seconds` ago, but it will
not be more recent.

See `event.Event` in [event.py](../event.py) for the column names and types
of the `Events` table.

## Adding a New Alert
Create a module in this package whose name is the canonical name of the new
alert.  Implement the `alert.Alert` abstract base class in that
module, and then register your implementation in [\_\_init\_\_.py](__init__.py)
(follow by example).

If your alert constructor takes any arguments (e.g. configuration), deduce the
arguments from relevant command line options in [tool.py](../tool.py) (see the
`analyze_log` function).
