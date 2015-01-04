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
    implementations for a JSON encoder and decoder and set the timezone
    of all datetimes to UTC.

    >>> dt = Datetime(2015, 1, 12, 11, 23, 46)
    >>> date = datetime.datetime(2015, 1, 12, 11, 23, 46,
    ...                          tzinfo=datetime.timezone.utc)
    >>> dt == date
    True
    """
    JSON_FORMAT = "%Y-%m-%d %H:%M:%S%z"

    def __new__(cls, *args, **kwargs):
        """
        All datetime instances are always initiated with timezone UTC
        whenever possible
        """
        try:
            return super().__new__(cls, *args, tzinfo=datetime.timezone.utc,
                                   **kwargs)
        except TypeError:
            return super().__new__(cls, *args, **kwargs)

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
    implementations for a JSON encoder and decoder.  Also, defined
    constants for common timedeltas like day, week and year.
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

Timedelta.HOUR = Timedelta(hours=1)
Timedelta.DAY = Timedelta(days=1)
Timedelta.WEEK = Timedelta(weeks=1)
