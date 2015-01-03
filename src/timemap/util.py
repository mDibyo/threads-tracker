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
    def from_json(cls, s: str or None):
        """
        Create a Datetime object from its JSON representation.

        :param s: JSON-encoded string for the Datetime object
        """
        return cls.strptime(s, cls.JSON_FORMAT)

    def to_json(self):
        """
        Convert object to a JSON-string representation.
        """
        return self.strftime(self.JSON_FORMAT)


class Timedelta(datetime.timedelta):
    """
    Subclass of datetime.timedelta defined in order to add
    implementations for a JSON encoder and decoder.
    """
    @classmethod
    def from_json(cls, f: float or None):
        """
        Create a Timedelta object from its JSON representation.

        :param f: JSON-encoded float for the Timedelta object
        """
        return cls(seconds=float(f))

    def to_json(self):
        """
        Convert object to a JSON-string representation.
        """
        return self.total_seconds()
