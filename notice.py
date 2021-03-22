"""routines for notices

A notice is emitted by the log monitor to indicate something of interest,
e.g. a periodic metrics summary or a triggered alert condition.

Notices have two output formats: JSON and pretty.  JSON is intended for
programmatic consumption, while pretty is intended for human eyeballs.
"""


import json
from tabulate import tabulate


def alert(name, is_triggered, message):
    return {
        'alert': {
            'name': name,
            'is_triggered': is_triggered,
            'message': message
        }
    }


def table(title, column_names, rows):
    return {
        'table': {
            'title': title,
            'column_names': column_names,
            'rows': rows
        }
    }


def to_pretty(notice):
    if 'alert' in notice:
        return 'TODO: pretty-format notices' # TODO
    
    assert 'table' in notice
    table = notice['table']
    return table['title'] + '\n' + tabulate(table['rows'], table['column_names'], tablefmt="fancy_grid")


def to_json(notice):
    return json.dumps(notice)
