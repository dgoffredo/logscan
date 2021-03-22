"""routines for log events"""


import dataclasses
import typing


@dataclasses.dataclass
class Event:
    # public IP address of the requester
    remote_host: str
    # when the request was received, in seconds since Unix epoch
    unix_time: int
    # the first line of the HTTP request (verb, resource, version, etc.)
    request: str
    # HTTP status in the response to the request
    response_status: int
    # total size, in bytes, of the response to the request
    response_bytes: int
    # the first path component of the resource referenced, e.g. "/users"
    section: str = dataclasses.field(init=False)

    def __post_init__(self):
        self.section = parse_section(self.request)


def field_names():
    return list(typing.get_type_hints(Event).keys())


def parse_section(request):
    """Return the first path component of the resource named in the specified
    HTTP `request`, e.g. for

        GET /api/user HTTP/1.0

    return

        /api

    Or, return `None` if there is no resource named in `request`.
    """
    try:
        return '/'.join(request.split()[1].split('/')[:2])
    except IndexError:
        return
