"""amount of repsonse data sent to each remote host"""


from .statistic import Statistic


class RemoteHostThroughput(Statistic):
    def period_seconds(self):
        return 10

    def title(self):
        return 'Top 10 Remote Hosts Data Throughput'

    def column_names(self):
        return ['Remote Host IP', 'Total Response Data (kilobytes)']

    def sql_query(self):
        return f"""
            select remote_host, sum(response_bytes) / 1024.0 as throughput
            from Events
            where unix_time >=
                (select max(unix_time) from Events) - {self.period_seconds()}
            group by remote_host
            order by throughput desc
            limit 10;
        """
