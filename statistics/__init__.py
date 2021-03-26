
statistics = {}

from . import top_sections
statistics['top_sections'] = top_sections.TopSections

from . import remote_host_throughput
statistics['remote_host_throughput'] = remote_host_throughput.RemoteHostThroughput

from . import response_statuses
statistics['response_statuses'] = response_statuses.ResponseStatuses

from .statistic import *
