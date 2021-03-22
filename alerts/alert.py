"""abstract base class for alerts"""


import abc
from typing import List


class Status:
    def __init__(self, triggered: bool, message: str):
        self.tiggered = triggered
        self.message = message


class Alert(abc.ABC):
    @abc.abstractmethod
    def sql_query(self) -> str:
        pass

    @abc.abstractmethod
    def handle_query_result(self, rows: List[tuple]) -> Status:
        pass
    
    @abc.abstractmethod
    def window_seconds(self) -> float:
        pass
