"""alert when the total requst volume over a period exceeds a threshold"""


from . import alert


_sql_template =  """
-- the timestamp at the beginning of the window
select max(unix_time) from Events
    where unix_time <= (select max(unix_time) from Events) - {seconds}

union all

-- the timestamp at the end of the window
select max(unix_time) from Events

union all

-- total count of events (requests) within the window
select count(*)
from Events
where unix_time >=
    (select max(unix_time) from Events
     where unix_time <= (select max(unix_time) from Events) - {seconds})
"""


WINDOW_SECONDS = 120


class TotalVolume(alert.Alert):
    def __init__(self, volume_threshold_per_second):
        self._volume_threshold_per_second = volume_threshold_per_second
        self._sql = _sql_template.format(seconds=WINDOW_SECONDS)

    def window_seconds(self):
        return WINDOW_SECONDS

    def sql_query(self):
        return self._sql

    def handle_query_result(self, rows):
        (begin_time,), (end_time,), (count,) = rows
        threshold = self._volume_threshold_per_second
        seconds = end_time - begin_time
        per_second = count / seconds
        
        if per_second <= threshold:
            message = f'total volume of requests was at or below {threshold} per second ({per_second:.2f} per second, {count} total) on average over the {seconds} seconds preceding Unix time {end_time}'
            return alert.Status(triggered=False, message=message)
        
        message = f'total volume of requests exceeded limit of {threshold} per second ({per_second:.2f} per second, {count} total) on average over the {seconds} seconds preceding Unix time {end_time}'
        return alert.Status(triggered=True, message=message)
