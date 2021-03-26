"""most frequently requested site sections"""


from .statistic import Statistic


class TopSections(Statistic):
    def period_seconds(self):
        return 10

    def title(self):
        return 'Top 10 Site Sections by Number of Requests'

    def column_names(self):
        return ['Site Section (from URL)', 'Number of Requests']

    def sql_query(self):
        return f"""
            select section, count(*) as frequency
            from Events
            where unix_time >=
                (select max(unix_time) from Events) - {self.period_seconds()}
            group by section
            order by frequency desc
            limit 10;
        """
