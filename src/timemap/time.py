#!/usr/bin/env python3

"""
This module contains classes representing time chunks which are to be
allocated to different tasks.

Module structure:
- TimeChunk
  - AllocatedTimeChunk
"""


import json

from timemap.util import Datetime, Timedelta


__author__ = "Dibyo Majumdar"
__email__ = "dibyo.majumdar@gmail.com"


class TimeChunk(object):
    """
    A TimeChunk is a chunk of time between two times.
    """
    def __init__(self,
                 start_time: Datetime,
                 duration: Timedelta=Timedelta(minutes=15)):
        self.start_time = start_time
        self._duration = duration

    @property
    def duration(self):
        """
        Get the duration of this time chunk.
        """
        return self._duration

    def to_json(self):
        """
        Convert to JSON representation.  It relies on JSON converters
        for timemap.util.Datetime and timemap.util.Timedelta to encode
        them as strings.
        """
        return {
            'start_time': self.start_time.to_json(),
            'duration': self._duration.to_json()
        }

    @staticmethod
    def json_to_dict(d: dict):
        """
        Convert the JSON representation of a time chunk to an object
        dictionary decoding strings for timemap.util.Datetime and
        timemap.util.Timedelta instances into corresponding instances.

        :param d: JSON dictionary representing the time chunk
        """
        d['start_time'] = Datetime.from_json(d['start_time'])
        d['duration'] = Timedelta.from_json(d.get('duration', None))

        return d

    @classmethod
    def from_json(cls, d: dict):
        """
        Create a TimeChunk instance from its JSON representation

        :param d: JSON dictionary for the time chunk
        """
        kwargs = cls.json_to_dict(d)

        return cls(**kwargs)


class AllocatedTimeChunk(TimeChunk):
    """
    An AllocatedTimeChunk is a TimeChunk that can be allocated to a
    particular task.
    """
    def __init__(self,
                 start_time: Datetime,
                 duration: Timedelta=Timedelta(minutes=15)):
        """
        :param start_time: the start time of the time chunk
        :param duration: the duration/size of the time chunk
        :return:
        """
        super(AllocatedTimeChunk, self).__init__(start_time, duration)
        self._task_allocated = None
        self._key = None

    def to_json(self):
        """
        Convert to JSON representation.  It is based almost completely
        on its definition in the superclass.
        """
        encoded = super(AllocatedTimeChunk, self).to_json()

        encoded['task_allocated'] = self._task_allocated
        encoded['key'] = self._key
        return encoded

    class AllocatedTimeChunkJSONDecoder(TimeChunk.TimeChunkJSONDecoder):
        """
        JSON decoder class for AllocatedTimeChunk subclassing
        TimeChunk.TimeChunkJSONDecoder.  It is reliant to a large
        extent on its superclass to whose state it adds its allocated
        task and the corresponding key.
        """
        def decode(self, s: str, _w=None):
            """
            Create a AllocatedTimeChunk instance from its JSON-encoded
            string representation.

            :param s: JSON-encoded string for the allocated time chunk
            :param _w: unused variable kept to match superclass method
                signature
            """
            kwargs = self.to_dict(s)

            allocatedTimeChunk = AllocatedTimeChunk(**kwargs)
            allocatedTimeChunk.set_task_assigned(**kwargs)

            return allocatedTimeChunk

    def set_task_assigned(self,
                          task_allocated: str,
                          key: int):
        """
        Set the uid of the task to which this time chunk has been
        allocated provided the correct key is provided.  The key is
        determined when this time chunk is first allocated to a task
        and ensures that only the initial allocator can reallocate the
        chunk.

        :param task_allocated: the task to which this time chunk is
        allocated
        :param key: the key to this time chunk
        :return:
        """
        if self._key is not None:
            if self._key != key:
                raise KeyError("Task key does not match. ")

        self._task_allocated = task_allocated

    def get_task_assigned(self):
        """
        Get the uid of the task to which this time chunk has been
        allocated.
        """
        return self._task_allocated
