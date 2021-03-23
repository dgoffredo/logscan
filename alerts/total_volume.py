"""alert when the total requst volume over a period exceeds a threshold"""


import .alert


_sql_template =  """
-- the timestamp at the beginning of the window
select max(unix_time)
    where unix_time <= (select max(unix_time) from Events) - {seconds}

union all

-- the timestamp at the end of the window
select max(unix_time) from Events

union all

-- total count of events (requests) within the window
select count(*)
from Events
where unix_time >=
    (select max(unix_time)
     where unix_time <= (select max(unix_time) from Events) - {seconds})
"""


class TotalVolume(alert.Alert):
    def __init__(self, window_seconds, volume_threshold):
        self._window_seconds = window_seconds
        self._volume_threshold = volume_threshold
        self._sql = _sql_template.format(seconds=window_seconds)

    def window_seconds(self):
        return self._window_seconds

    def sql_query(self):
        return self._sql

    def handle_query_result(self, rows):
        (begin_time,), (end_time,), (count,) = rows
        threshold = self._volume_threshold
        window_seconds = self._window_seconds
        scaled_count = window_seconds / (end_time - begin_time) * count
        
        if scaled_count <= threshold:
            message = f'total volume of requests was at or below {threshold} ({scaled_count}) on average over the {window_seconds} seconds preceding Unix time {end_time}'
            return alert.Status(triggered=False, message=message)
        
        message = f'total volume of requests exceeded limit of {threshold} ({scaled_count}) on average over the {window_seconds} seconds preceding Unix time {end_time}'
        return alert.Status(triggered=True, message=message)
