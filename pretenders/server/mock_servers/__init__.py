from datetime import timedelta, datetime
import json

from pretenders.common.constants import FOREVER


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

    def __init__(self, start, name, timeout, last_call, protocol):
        self.__dict__.update({
            'start': start,
            'timeout': timeout,
            'last_call': last_call,
            'name': name,
            'protocol': protocol,
        })

    def __str__(self):
        return (
            "Name: {name}, last_call: {last_call}, timeout: {timeout}".format(
                **self.__dict__)
        )

    @classmethod
    def from_json_response(cls, response_data):
        """
        Create an instance from the body of a JSON response.
        """
        data = json.loads(response_data.decode('ascii'))
        data['start'] = get_datetime_from_string(data['start'])
        data['last_call'] = get_datetime_from_string(data['last_call'])
        if data['timeout'] != FOREVER:
            data['timeout'] = get_timedelta_from_string(data['timeout'])
        return cls(**data)

    def as_dict(self):
        return {
            'start': str(self.start),
            'timeout': str(self.timeout),
            'last_call': str(self.last_call),
            'name': str(self.name),
            'protocol': self.protocol
        }

    def as_json(self):
        """Convert to JSON."""
        return json.dumps(self.as_dict())

    def keep_alive(self):
        "Refresh the last_call date to keep this server up"
        self.last_call = datetime.now()

    @property
    def is_expired(self):
        return (self.timeout != FOREVER and
                datetime.now() - self.last_call > self.timeout)
