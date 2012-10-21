from datetime import timedelta, datetime

import json


def get_timedelta_from_string(string):
    data = string.split(":")
    time = timedelta(hours=int(data[0]),
                     minutes=int(data[1]),
                     seconds=float(data[2]))
    return time


def get_datetime_from_string(date_string):
    return datetime.strptime(date_string.split('.')[0],
                             "%Y-%m-%d %H:%M:%S")


class PretenderModel(object):
    """Information related to a spawned pretender."""

    def __init__(self, start, uid, timeout, last_call):
        self.__dict__.update({
            'start': start,
            'uid': uid,
            'timeout': timeout,
            'last_call': last_call,
        })

    def __str__(self):
        return "UID: {0}, last_call: {1}, timeout: {2}".format(
                self.uid, self.last_call, self.timeout)

    @classmethod
    def from_json_response(cls, response):
        """
        Create an instance from the body of a JSON response.
        """
        data = json.loads(response.read().decode('ascii'))
        data['start'] = get_datetime_from_string(data['start'])
        data['last_call'] = get_datetime_from_string(data['last_call'])
        data['timeout'] = get_timedelta_from_string(data['timeout'])
        return cls(**data)

    def as_json(self):
        """Convert to JSON."""
        json_data = {
            'start': str(self.start),
            'uid': self.uid,
            'timeout': str(self.timeout),
            'last_call': str(self.last_call),
        }
        return json.dumps(json_data)

    def keep_alive(self):
        "Refresh the last_call date to keep this server up"
        self.last_call = datetime.now()

    @property
    def timeout_in_secs(self):
        return self.timeout.seconds
