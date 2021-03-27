# Statistics
A statistic is a SQL query whose result set is rendered as a table for display.

Each statistic has a `period_seconds`: the number of seconds back in time from
the most recent event that the statistic requires to be able to see.  The
horizon (oldest event) of the `Events` table in the sqlite database on which
the query is executed may be older than `period_seconds` ago, but it will
not be more recent.

See `event.Event` in [event.py](../event.py) for the column names and types
of the `Events` table.

Each statistic is calculated and displayed at most once each `period_seconds`.

## Adding a New Statistic
Create a module in this package whose name is the canonical name of the new
statistic.  Implement the `statistic.Statistic` abstract base class in that
module, and then register your implementation in [\_\_init\_\_.py](__init__.py)
(follow by example).
