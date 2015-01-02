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

    class TimeChunkJSONEncoder(json.JSONEncoder):
        """
        JSON encoder class for TimeChunk subclassing json.JSONEncoder.
        It relies on custom JSON encoder classes for timemap.util.Datetime
        and timemap.util.Timedelta (which are defined inside the
        corresponding classes) to encode them as strings.
        """
        def default(self, o: TimeChunk):
            """
            Convert object to JSON-serializable dictionary.

            :param o: the TimeChunk object to be encoded
            """
            return {
                'start_time': Datetime.DatetimeJSONEncoder().
                encode(o.start_time),
                'duration': Timedelta.TimedeltaJSONEncoder().
                encode(o._duration)
            }

    class TimeChunkJSONDecoder(json.JSONDecoder):
        """
        JSON decoder class for TimeChunk subclassing json.JSONDecoder.
        It relies on custom JSON decoder classes for timemap.util.Datetime
        and timemap.util.Timedelta (which are defined inside the
        corresponding classes) to decode them from encoded strings.
        """
        @staticmethod
        def to_dict(s: str):
            """
            Convert the JSON-encoded string for a time chunk to a
            dictionary and then decode strings for timemap.util.Datetime
            and timemap.util.Timedelta instances into corresponding
            instances.

            :param s: JSON-encoded string for the time chunk
            """
            d = json.loads(s)

            d['start_time'] = Datetime.DatetimeJSONDecoder().\
                decode(d['start_time'])
            d['duration'] = Timedelta.TimedeltaJSONDecoder().\
                decode(d['duration'])

            return d

        def decode(self, s: str, _w=None):
            """
            Create a TimeChunk instance from its JSON-encoded string
            representation.

            :param s: JSON-encoded string for the time chunk.
            :param _w: unused variable kept to match superclass method
                signature
            """
            kwargs = json.loads(s)

            return TimeChunk(**kwargs)


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
        self.key = None

    class AllocatedTimeChunkJSONEncoder(TimeChunk.TimeChunkJSONEncoder):
        """
        JSON encoder class for AllocatedTimeChunk subclassing
        TimeChunk.TimeChunkJSONEncoder.  It is reliant to a large
        extent on its superclass to whose state it adds its allocated
        task and the corresponding key.
        """
        def default(self, o: AllocatedTimeChunk):
            """
            Convert object to JSON-serializable dictionary.

            :param o: the AllocatedTimeChunk object to be encoded
            """
            encoded = \
                super(AllocatedTimeChunk.AllocatedTimeChunkJSONEncoder, self).\
                default(o)

            encoded['task_allocated'] = o._task_allocated \
                if o._task_allocated else None
            encoded['key'] = o.key if o._task_allocated else None

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
        if self.key is not None:
            if self.key != key:
                raise KeyError("Task key does not match. ")

        self._task_allocated = task_allocated

    def get_task_assigned(self):
        """
        Get the uid of the task to which this time chunk has been
        allocated.
        """
        return self._task_allocated
