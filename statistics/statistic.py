"""abstract base class for statistics"""


import abc
import typing


class Statistic(abc.ABC):
    @abc.abstractmethod
    def period_seconds(self) -> float:
        pass

    @abc.abstractmethod
    def title(self) -> str:
        pass

    @abc.abstractmethod
    def column_names(self) -> typing.Sequence[str]:
        pass

    @abc.abstractmethod
    def sql_query(self) -> str:
        pass
