#!/usr/bin/env python3

"""
This module defines various time-related subclasses and methods to be
utilized in other modules.

Module structure:
- UTC(datetime.tzinfo)
- Datetime(datetime.datetime)
- Timedelta(datetime.timedelta)
"""

import datetime
import json


__author__ = "Dibyo Majumdar"
__email__ = "dibyo.majumdar@gmail.com"


class UTC(datetime.tzinfo):
    """
    Timezone info subclassing the abstract datetime.tzinfo class and
    representing the UTC timezone.  Implementations are supplied for
    for utcoffset and tzname which represent the state of the timezone.
    """
    def utcoffset(self, dt: datetime.datetime):
        return 0

    def tzname(self, dt):
        return "UTC"


class Datetime(datetime.datetime):
    """
    Subclass of datetime.datetime defined in order to add
    implementations for a JSON encoder and decoder.

    >>> dt = Datetime(2015, 1, 12, 11, 23, 46, tzinfo=datetime.timezone.utc)
    >>> date = datetime.datetime(2015, 1, 12, 11, 23, 46,
    ...                          tzinfo=datetime.timezone.utc)
    >>> dt == date
    True
    """
    JSON_FORMAT = "%Y-%m-%d %H:%M:%S%z"

    @classmethod
    def from_json(cls, s: str):
        """
        Create a Datetime object from its JSON representation.

        :param s: JSON-encoded string for the Datetime object
        """
        return cls.strptime(s, cls.JSON_FORMAT)

    def for_json(self):
        """
        Convert object to a JSON-string representation.
        """
        return self.strftime(self.JSON_FORMAT)

    class DatetimeJSONEncoder(json.JSONEncoder):
        """
        JSON encoder class for Datetime subclassing json.JSONEncoder.
        It represents the object as a formatted string.
        """
        def default(self, o: "Datetime"):
            """
            Convert object to string.

            :param o: the Datetime object to be encoded
            """
            return o.for_json() if o is not None else None

    class DatetimeJSONDecoder(json.JSONDecoder):
        """
        JSON decoder class for Datetime subclassing json.JSONDecoder.
        Object is represented in JSON as a formatted string.
        """
        def decode(self, s: str, _w=None):
            """
            Create a Datetime instance from its JSON-encoded string
            representation.

            :param s: JSON-encoded string for the Datetime object.
            :param _w: unused variable kept to match superclass method
                signature
            """
            obj = json.loads(s)
            return Datetime.from_json(obj) if obj is not None else None


class Timedelta(datetime.timedelta):
    """
    Subclass of datetime.timedelta defined in order to add
    implementations for a JSON encoder and decoder.
    """
    @classmethod
    def from_json(cls, f: float):
        """
        Create a Timedelta object from its JSON representation.

        :param f: JSON-encoded float for the Timedelta object
        """
        return cls(seconds=float(f))

    def for_json(self):
        """
        Convert object to a JSON-string representation.
        """
        return self.total_seconds()

    class TimedeltaJSONEncoder(json.JSONEncoder):
        """
        JSON encoder class for Timedelta subclassing json.JSONEncoder.
        It represents the object as the number of seconds it is.
        """
        def default(self, o: "Timedelta"):
            """
            Convert object to integer.

            :param o: the Timedelta object to be encoded
            """
            return o.for_json() if o is not None else None

    class TimedeltaJSONDecoder(json.JSONDecoder):
        """
        JSON decoder class for Timedelta subclassing json.JSONDecoder.
        Object is represented in JSON as the number of seconds it is.
        """
        def decode(self, f: float, _w=None):
            """
            Create a Timedelta instance from its JSON-encoded float
            representation.

            :param f: JSON-encoded float for the Timedelta object.
            :param _w: unused variable kept to match superclass method
                signature
            """
            obj = json.loads(f)
            return Timedelta.from_json(obj) if obj is not None else None
