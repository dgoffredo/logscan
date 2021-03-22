"""alert when the total requst volume over a period exceeds a threshold"""


import .alert

# The first row returned is the total number of events (HTTP requests) within
# the last "?" seconds. The second row returned is the greatest Unix time so
# far.
# Note that this query implicitly assumes that the table "Events" is not empty.
_sql_template =  """
select count(*)
from Events
where unix_time >= (select max(unix_time) from Events) - {}

union all

select max(unix_time) from Events;
"""


class TotalVolume(alert.Alert):
    def __init__(self, window_seconds, volume_threshold):
        self._window_seconds = window_seconds
        self._volume_threshold = volume_threshold
        self._sql = _sql_template.format(window_seconds)

    def window_seconds(self):
        return self._window_seconds

    def sql_query(self):
        return self._sql

    def handle_query_result(self, rows):
        (count,), (largest_unix_time,) = rows
        threshold = self._volume_threshold
        
        if count <= threshold:
            # It's not necessarily a recovery, but each time we are below the
            # threshold, we produce a message that says we recovered.  The
            # calling code will use the message only if we were previously
            # triggered.
            recovery = f'total volume of requests recovered: fell below {threshold} ({count}) over the {self._window_seconds} seconds preceding Unix timestamp {largest_unix_time}'
            return alert.Status(triggered=False, message=recovery)
        
        message = f'total volume of requests exceeds limit of {threshold} ({count}) over the {self._window_seconds} seconds preceding Unix timestamp {largest_unix_time}'
        return alert.Status(triggered=True, message=message)
