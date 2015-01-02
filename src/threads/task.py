#!/usr/bin/env python3

"""
This module contains classes representing different types of tasks.

Module structure:
- Task
  - Event
  - Assignment

"""

import uuid
import json
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
    >>> s = Task.TaskJSONEncoder().encode(t)
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

    class TaskJSONEncoder(json.JSONEncoder):
        """
        JSON encoder class for Task subclassing json.JSONEncoder.  It
        relies on custom JSON encoder classes for timemap.util.Datetime
        and timemap.util.Timedelta (which are defined inside the
        corresponding classes) to encode them as strings.

        >>> import datetime
        >>> dt = Datetime(2015, 1, 12, 11, 23, 46,
        ...               tzinfo=datetime.timezone.utc)
        >>> t = Task("try out this cool thing", dt)
        >>> s = Task.TaskJSONEncoder().encode(t)
        >>> t_new = Task.TaskJSONDecoder().decode(s)
        >>> t_new == t
        True
        """
        def default(self, o: "Task"):
            """
            Convert object to JSON-serializable dictionary.

            :param o: the Task object to be encoded
            """
            return {
                'uid': o.uid,
                'name': o.name,
                'start_time': Datetime.DatetimeJSONEncoder().
                encode(o.start_time),
                'end_time': Datetime.DatetimeJSONEncoder().encode(o.end_time),
                'importance': o.importance,
                'repeating': o.repeating,
                'period': Timedelta.TimedeltaJSONEncoder().encode(o.period),
                'partial_completion': o.partial_completion,
                'max_divisions': o.max_divisions,
                'thread_name': o.thread_name
            }

    class TaskJSONDecoder(json.JSONDecoder):
        """
        JSON decoder class for Task subclassing json.JSONDecoder.  It
        relies on custom JSON decoder classes for timemap.util.Datetime
        and timemap.util.Timedelta (which are defined inside the
        corresponding classes) to decode them from encoded strings.
        """
        @staticmethod
        def to_dict(s: str):
            """
            Convert the JSON-encoded string for a task to a dictionary
            and then decode strings for timemap.util.Datetime and
            timemap.util.Timedelta instances into corresponding instances.

            :param s: JSON-encoded string for the task
            """
            d = json.loads(s)

            d['start_time'] = Datetime.DatetimeJSONDecoder().\
                decode(d.get('start_time', None))
            d['end_time'] = Datetime.DatetimeJSONDecoder().\
                decode(d.get('end_time', None))
            d['period'] = Timedelta.TimedeltaJSONDecoder().\
                decode(d.get('period', None))

            uid = d.get('uid', None)
            del d['uid']

            return uid, d

        def decode(self, s: str, _w=None):
            """
            Create a Task instance from its JSON-encoded string
            representation.

            :param s: JSON-encoded string for the task.
            :param _w: unused variable kept to match superclass method
                signature
            """
            uid, kwargs = self.to_dict(s)

            task = Task(**kwargs)
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

    class EventJSONEncoder(Task.TaskJSONEncoder):
        """
        JSON encoder class for Event subclassing Task.TaskJSONEncoder.
        It is reliant almost completely on its superclass only
        deviating from it because it represents only a subset of tasks
        (ie. events).
        """
        def default(self, o: "Event"):
            """
            Convert object to JSON-serializable dictionary and record
            task type (ie. event) in it.

            :param o: the event object to be encoded
            """
            encoded = super(Event.EventJSONEncoder, self).default(o)

            encoded['type'] = 'event'
            return encoded

    class EventJSONDecoder(Task.TaskJSONDecoder):
        """
        JSON decoder class for Event subclassing Task.TaskJSONDecoder.
        It is reliant almost completely on its superclass only
        deviating from it because it represents only a subset of tasks
        (ie. events).
        """
        def decode(self, s: str, _w=None):
            """
            Create an Event instance from its JSON-encoded string
            representation.

            :param s: JSON-encoded string for the event.
            :param _w: unused variable kept to match superclass method
                signature
            """
            uid, kwargs = Task.TaskJSONDecoder.to_dict(s)

            event = Event(**kwargs)
            event.uid = uid if uid is not None else uuid.uuid4()

            return event


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

    class AssignmentJSONEncoder(Task.TaskJSONEncoder):
        """
        JSON encoder class for Assignment subclassing
        Task.TaskJSONEncoder.  It is reliant to a large extent on its
        superclass.  It deviates because it represents only a subset of
        tasks (ie. assignments) and therefore, has a deadline.
        """
        def default(self, o: "Assignment"):
            """
            Convert object to JSON-serializable dictionary and record
            task type (ie. assignment) in it.

            :param o: the assignment object to be encoded
            """
            encoded = super(Assignment.AssignmentJSONEncoder, self).default(o)

            encoded['deadline'] = Datetime.DatetimeJSONEncoder().\
                encode(o.deadline)
            encoded['expected_duration'] = Timedelta.\
                TimedeltaJSONEncoder().encode(o.expected_duration)

            encoded['type'] = 'assignment'
            return encoded

    class AssignmentJSONDecoder(Task.TaskJSONDecoder):
        """
        JSON decoder class for Assignment subclassing
        Task.TaskJSONDecoder.  It is reliant to a large extent on its
        superclass.  It deviates because it represents only a subset of
        tasks (ie. assignments) and therefore, has a deadline.
        """
        @staticmethod
        def to_dict(s: str):
            """
            Convert the JSON-encoded string for an assignment to a
            dictionary and then decode strings for timemap.util.Datetime
            and timemap.util.Timedelta instances into corresponding
            instances.  It relies to a large extent on the
            corresponding superclass method.

            :param s: JSON-encoded string for the task
            """
            uid, d = Task.TaskJSONDecoder.to_dict(s)

            d['deadline'] = Datetime.DatetimeJSONDecoder().\
                decode(d.get('deadline'))
            d['expected_duration'] = Timedelta.TimedeltaJSONDecoder().\
                decode(d.get('expected_duration', None))

            return uid, d

        def decode(self, s: str, _w=None):
            """
            Create an Assignment instance from its JSON-encoded string
            representation.

            :param s: JSON-encoded string for the assignment.
            :param _w: unused variable kept to match superclass method
                signature
            """
            uid, kwargs = self.to_dict(s)

            assignment = Assignment(**kwargs)
            assignment.uid = uid if uid is not None else uuid.uuid4()

            return assignment

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
