from datetime import timedelta, datetime

import json


def get_timedelta_from_string(string):
    data = string.split(":")
    time = timedelta(
        hours=int(data[0]),
        minutes=int(data[1]),
        seconds=float(data[2]))
    return time


def get_datetime_from_string(date_string):
    return datetime.strptime(date_string.split('.')[0],
                             "%Y-%m-%d %H:%M:%S")


class PretenderModel(object):
    """Information related to a spawned pretender."""

    def __init__(self, start, port, pid, uid, timeout, last_call, type):
        self.data = {
            'start': start,
            'port': port,
            'pid': pid,
            'uid': uid,
            'timeout': timeout,
            'last_call': last_call,
            'type': type,
        }

    def __str__(self):
        return str(self.data)

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise AttributeError("{0} is not an field in data".format(key))

    @classmethod
    def from_json_response(cls, response):
        """Create an instance from the body of a JSON response."""
        creating_dict = json.loads(response.read().decode('ascii'))
        creating_dict['start'] = get_datetime_from_string(
                                    creating_dict['start'])
        creating_dict['last_call'] = get_datetime_from_string(
                                        creating_dict['last_call'])
        creating_dict['timeout'] = get_timedelta_from_string(
                                        creating_dict['timeout'])
        return cls(**creating_dict)

    def as_json(self):
        """Convert to JSON."""
        json_data = {}
        json_data.update(self.data)
        json_data['start'] = str(json_data['start'])
        json_data['last_call'] = str(json_data['last_call'])
        json_data['timeout'] = str(json_data['timeout'])
        return json.dumps(json_data)

    def keep_alive(self):
        "Refresh the last_call date to keep this server up"
        self.data['last_call'] = datetime.now()

    @property
    def timeout_in_secs(self):
        return self.timeout.seconds
