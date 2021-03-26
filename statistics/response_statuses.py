"""frequency of response statuses (e.g. how many 404s)"""


from .statistic import Statistic


class ResponseStatuses(Statistic):
    def period_seconds(self):
        return 10

    def title(self):
        return 'HTTP Response Statuses'

    def column_names(self):
        return ['HTTP Response Status', 'Number of Requests']

    def sql_query(self):
        return f"""
            select response_status, count(*) as frequency
            from Events
            where unix_time >=
                (select max(unix_time) from Events) - {self.period_seconds()}
            group by response_status
            order by frequency desc;
        """

