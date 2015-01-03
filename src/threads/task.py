#!/usr/bin/env python3

"""
This module contains classes representing different types of tasks.

Module structure:
- Task
  - Event
  - Assignment

"""

import uuid
from timemap.util import Datetime, Timedelta


__author__ = "Dibyo Majumdar"
__email__ = "dibyo.majumdar@gmail.com"


class Task(object):
    """
    Represents a task.  This serves as the base class of all typed of
    tasks. It is also the final representation of all tasks in the
    created schedule.

    >>> import datetime
    >>> dt = Datetime(2015, 1, 12, 11, 23, 46,
    ...               tzinfo=datetime.timezone.utc)
    >>> t = Task("try out this cool thing", dt)
    >>> print(t)
    Task: try out this cool thing in 2015-01-12 11:23:46+00:00-None
    """

    def __init__(self,
                 name: str,
                 start_time: Datetime=None,
                 end_time: Datetime=None,
                 importance: float=5,
                 repeating: bool=False,
                 period: Timedelta=None,
                 partial_completion: bool=False,
                 max_divisions: int=-1,
                 thread_name: str=None):
        """
        :param name: the name of the task
        :param start_time: the start time of the task
        :param end_time: the end time of the task
        :param importance: the importance given to the task
        :param repeating: whether the task is repeating
        :param period: the period of repetition of the task
        :param partial_completion: whether partial completion is useful
        :param max_divisions: the maximum number of non-consecutive
            time chunks that the task can be divided into
        :param thread_name: the name of the thread to which this task
            belongs
        """
        self.uid = str(uuid.uuid4())
        self.name = name
        self.start_time = self.end_time = None
        self._importance = importance
        self.repeating = repeating
        self.period = period
        self.partial_completion = partial_completion
        self.max_divisions = max_divisions
        self.thread_name = thread_name

        if start_time:
            self.change_time(start_time, end_time)

    def __str__(self):
        """
        Return string representation of self.
        """
        return "Task: '{0.name}' in {0.start_time}-{0.end_time}".format(self)

    def __eq__(self, other: "Task"):
        """
        Check equality of two tasks by checking if their uid is the same.

        :param other: the other task to be compared
        """
        return self.uid == other.uid

    def to_json(self):
        """
        Convert to JSON representation.  It relies on JSON converters
        for timemap.util.Datetime and timemap.util.Timedelta to encode
        them as strings.

        >>> import datetime
        >>> dt = Datetime(2015, 1, 12, 11, 23, 46,
        ...               tzinfo=datetime.timezone.utc)
        >>> t = Task("try out this cool thing", dt)
        >>> d = t.to_json()
        >>> t_new = Task.from_json(d)
        >>> t_new == t
        True
        """
        return {
            'uid': self.uid,
            'name': self.name,
            'start_time': self.start_time.to_json(),
            'end_time': self.end_time.to_json(),
            'importance': self.importance,
            'repeating': self.repeating,
            'period': self.period.to_json(),
            'partial_completion': self.partial_completion,
            'max_divisions': self.max_divisions,
            'thread_name': self.thread_name
        }

    @staticmethod
    def json_to_dict(d: dict):
        """
        Convert the JSON representation of a task to an object
        dictionary decoding strings for timemap.util.Datetime and
        timemap.util.Timedelta instances into corresponding instances.

        :param d: JSON dictionary representing the task
        """
        d['start_time'] = Datetime.from_json(d.get('start_time', None))
        d['end_time'] = Datetime.from_json(d.get('end_time', None))
        d['period'] = Timedelta.from_json(d.get('period', None))

        return d

    @classmethod
    def from_json(cls, d: dict):
        """
        Create a Task instance from its JSON representation

        :param d: JSON dictionary for the task
        """
        kwargs = cls.json_to_dict(d)

        uid = kwargs.pop('uid', None)

        task = cls(**kwargs)
        task.uid = uid if uid is not None else uuid.uuid4()

        return task

    def change_time(self,
                    new_start_time: Datetime,
                    new_end_time: Datetime=None):
        """
        Change the start and (optionally) end time of a task.

        :param new_start_time: the new start time of the task
        :param new_end_time: the new end time of the task
        """
        if new_end_time:
            if new_start_time > new_end_time:
                raise Exception("Invalid time range for task. ")
        elif self.end_time:
            new_end_time = new_start_time + (self.end_time - self.start_time)

        self.start_time = new_start_time
        self.end_time = new_end_time

    @property
    def importance(self):
        return self._importance

    @importance.setter
    def importance(self, new_importance: float):
        """
        Change the importance of a task

        :param new_importance: the new importance of the task
        """
        if 0 <= new_importance <= 10:
            self._importance = new_importance
        else:
            raise Exception("Invalid importance for task. ")

    @importance.deleter
    def importance(self):
        del self._importance


class Event(Task):
    """
    Represents an event running between two fixed times.  This type of
    task represents a static task ie..one which can not be moved around
    in time.
    """

    def __init__(self,
                 name: str,
                 start_time: Datetime,
                 end_time: Datetime,
                 importance: float=5,
                 repeating: bool=False,
                 period: Timedelta=None,
                 partial_completion: bool=False,
                 max_divisions: int=-1):
        """
        :param name: the name of the event
        :param start_time: the start time of the event
        :param end_time: the end time of the event
        :param importance: the importance given to the task
        :param repeating: whether the task is repeating
        :param period: the period of repetition of the task
        :param partial_completion: whether partial completion is useful
        :param max_divisions: the maximum number of non-consecutive
            time chunks that the task can be divided into
        """
        super(Event, self).__init__(name, start_time, end_time, importance,
                                    repeating, period, partial_completion,
                                    max_divisions)

    def __str__(self):
        """
        Return string representation of self,
        """
        return "Event: '{0.name}' in {0.start_time}-{0.end_time}".format(self)

    def to_json(self):
        """
        Convert to JSON representation.  It is based almost completely
        on its definition in the superclass.
        """
        encoded = super(Event, self).to_json()

        encoded['type'] = 'event'
        return encoded


class Assignment(Task):
    """
    Represents an assignment with a time deadline.  This type of task
    represents a dynamic task ie. one which can be moved around within
    well-defined ranges, usually now and the deadline.
    """

    def __init__(self,
                 name: str,
                 deadline: Datetime,
                 expected_duration: Timedelta=None,
                 importance: float=5,
                 repeating: bool=False,
                 period: Timedelta=None,
                 partial_completion: bool=False,
                 max_divisions: int=-1):
        """
        :param name: the name of the event
        :param deadline: the time at which the assignment is due
        :param expected_duration: the expected time required to
            complete the assignment
        :param importance: the importance given to the task
        :param repeating: whether the task is repeating
        :param period: the period of repetition of the task
        :param partial_completion: whether partial completion is useful
        :param max_divisions: the maximum number of non-consecutive
            time chunks that the task can be divided into
        """
        super(Assignment, self).__init__(name,
                                         importance=importance,
                                         repeating=repeating,
                                         period=period,
                                         partial_completion=partial_completion,
                                         max_divisions=max_divisions)
        self.deadline = deadline
        self.expected_duration = expected_duration

    def __str__(self):
        """
        Return string representation of self,
        """
        return "Assignment: '{0.name}' by {0.deadline}".format(self)

    def to_json(self):
        """
        Convert to JSON representation.  It is reliant to a large
        extent on its implementation in the superclass.
        """
        encoded = super(Assignment, self).to_json()

        encoded['deadline'] = self.deadline.to_json()
        encoded['expected_duration'] = self.expected_duration.to_json()
        encoded['type'] = 'assignment'

        return encoded

    @staticmethod
    def json_to_dict(d: dict):
        """
        Convert the JSON representation of an assignment to an object
        dictionary decoding strings for timemap.util.Datetime and
        timemap.util.Timedelta instances into corresponding instances.

        :param d: JSON dictionary representing the task
        """
        d = Task.json_to_dict(d)

        d['deadline'] = Datetime.from_json(d.get('deadline', None))
        d['expected_duration'] = Timedelta.from_json(d.get('expected_duration',
                                                           None))

        return d

    def change_time(self,
                    new_start_time: Datetime,
                    new_end_time: Datetime=None):
        """
        Change the start and (optionally) end time of a assignment.
        Also change the expected duration of the assignment if
        appropriate.

        :param new_start_time: the new start time of the task
        :param new_end_time: the new end time of the task
        """
        super(Assignment, self).change_time(new_start_time, new_end_time)

        if self.end_time:
            self.expected_duration = self.end_time - self.start_time

        # Warn if deadline not met
        if self.start_time + self.expected_duration > self.deadline:
            print("WARNING: Deadline not met for {}".format(str(self)))
