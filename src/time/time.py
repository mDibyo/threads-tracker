__author__ = 'dibyo'

from datetime import datetime, timedelta
from thread.task import Task


class TimeChunk(object):
    """
    A TimeChunk is a chunk of time between two times.
    """
    def __init__(self,
                 start_time: datetime,
                 duration: timedelta=timedelta(minutes=15)):
        self.start_time = start_time
        self._duration = duration

    @property
    def duration(self) -> timedelta:
        """
        Get the duration of this time chunk.
        """
        return self._duration


class AllocatedTimeChunk(TimeChunk):
    """
    An AllocatedTimeChunk is a TimeChunk that can be allocated to a
    particular task.
    """
    def __init__(self,
                 start_time: datetime,
                 duration: timedelta=timedelta(minutes=15)):
        super(AllocatedTimeChunk, self).__init__(start_time, duration)
        self._task_assigned = None
        self.key = None

    def set_task_assigned(self,
                          task_assigned: Task,
                          key: int):
        if self.key is not None:
            if self.key != key:
                raise KeyError("Task key does not match. ")

        self._task_assigned = task_assigned

    def get_task_assigned(self):
        return self._task_assigned

