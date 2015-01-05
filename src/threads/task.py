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
from timemap.time import TimeChunk


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
                 partial_completion: bool=False,
                 max_divisions: int=-1,
                 thread_name: str=None):
        """
        :param name: the name of the task
        :param start_time: the start time of the task
        :param end_time: the end time of the task
        :param importance: the importance given to the task
        :param partial_completion: whether partial completion is useful
        :param max_divisions: the maximum number of non-consecutive
            time chunks that the task can be divided into
        :param thread_name: the name of the thread to which this task
            belongs
        """
        self.uid = uuid.uuid4()
        self.name = name
        self.start_time = self.end_time = None
        self._importance = importance
        self.partial_completion = partial_completion
        self.max_divisions = max_divisions
        self.thread_name = thread_name
        self.completed = False

        if start_time:
            self.change_time(start_time, end_time)

    def __str__(self):
        """
        Return string representation of self.
        """
        return "Task: '{0.name}' in {0.start_time}-{0.end_time}".format(self)

    def __eq__(self, other: "Task"):
        """
        Check equality of two tasks by checking if their uid is the
        same

        :param other: the other task to be compared
        """
        return self.uid == other.uid

    def __ne__(self, other: "Task"):
        """
        Check inequality of two tasks by checking if their uid is not
        the same

        :param other: the other task to be compared
        """
        return self.uid != other.uid

    def __hash__(self):
        """
        Return hash of the task.  The uid of the task is taken as its hash.
        """
        return int(self.uid)

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
            'uid': str(self.uid),
            'name': self.name,
            'start_time': self.start_time.to_json(),
            'end_time': self.end_time.to_json(),
            'importance': self.importance,
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

        return d

    @classmethod
    def from_json(cls, d: dict):
        """
        Create a Task instance from its JSON representation

        :param d: JSON dictionary for the task
        """
        kwargs = cls.json_to_dict(d)

        uid_str = kwargs.pop('uid', None)

        task = cls(**kwargs)
        task.uid = uuid.UUID(uid_str) if uid_str is not None else uuid.uuid4()

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
        """
        Get or set the importance of a task.  Importance should be a
        float in the range [0, 10].
        """
        return self._importance

    @importance.setter
    def importance(self, new_importance: float):
        if 0 <= new_importance <= 10:
            self._importance = new_importance
        else:
            raise Exception("Invalid importance for task. ")

    @importance.deleter
    def importance(self):
        del self._importance

    def complete(self):
        """
        Complete the task.
        """
        self.completed = True

    def is_done(self):
        """
        Return if the task is done.  A task is done if it has been
        completed or if its end time is in the past.
        """
        if self.end_time:
            if self.end_time < Datetime.now(self.end_time.tzinfo):
                return True

        return self.completed


class RepeatableTask(Task):
    def __init__(self,
                 name: str,
                 start_time: Datetime=None,
                 end_time: Datetime=None,
                 importance: float=5,
                 repeat: RepeatableTask.TaskRepeat=False,
                 partial_completion: bool=False,
                 max_divisions: int=-1,
                 thread_name: str=None):
        """
        :param name: the name of the task
        :param start_time: the start time of the task
        :param end_time: the end time of the task
        :param importance: the importance given to the task
        :param repeat: TaskRepeat object representing repeat status
        :param partial_completion: whether partial completion is useful
        :param max_divisions: the maximum number of non-consecutive
            time chunks that the task can be divided into
        :param thread_name: the name of the thread to which this task
            belongs
        """
        # Handle repeat object and the variables start_time and end_time
        self.repeat = repeat

        self._start_time = self._end_time = None

        if self.start_time is not None and self.end_time is not None:
            start_time = self.start_time
            end_time = self.end_time

        super().__init__(name=name,
                         start_time=start_time,
                         end_time=end_time,
                         importance=importance,
                         partial_completion=partial_completion,
                         max_divisions=max_divisions,
                         thread_name=thread_name)

    class TaskRepeat(object):
        """
        Store whether the task is repeating and, if so, the period of
        repetition.  It also stores and provides information about
        the start and stop of all the periods of the task.
        """
        def __init__(self,
                     repeat: bool=False,
                     period: Timedelta=None):
            """
            :param repeat: whether the task is repeating
            :param period: the period of repetition
            """
            self.repeat = repeat
            self.period = period

            if self.repeat:
                self.start_time = self.end_time = None

        def __bool__(self):
            """
            Return if the task is repeating.
            """
            return self.repeat

        def to_json(self):
            """
            Convert to JSON representation.  It relies on JSON
            converters for timemap.util.Datetime and
            timemap.util.Timedelta to encode them as strings.
            """
            if not self:
                return False

            return {
                'repeat': self.repeat,
                'period': self.period.to_json(),
                'start_time': self.start_time.to_json(),
                'end_time': self.end_time.to_json()
            }

        @staticmethod
        def json_to_dict(d: dict or bool):
            """
            Convert the JSON representation of a TaskRepeat to an
            object dictionary decoding strings for
            timemap.util.Datetime and timemap.util.Timedelta instances
            into corresponding instances.

            :param d: JSON dictionary representing the task
            """
            if isinstance(d, bool):
                return d

            d['period'] = Datetime.from_json(d.get('period', None))
            d['start_time'] = Datetime.from_json(d.get('start_time', None))
            d['end_time'] = Datetime.from_json(d.get('end_time', None))

            return d

        @classmethod
        def from_json(cls, d: dict or bool):
            """
            Create a TaskRepeat object from its JSON representation

            :param d: JSON dictionary for the TaskRepeat object
            """
            kwargs = cls.json_to_dict(d)

            if not kwargs:
                return cls()

            start_time = kwargs.pop('start_time', None)
            end_time = kwargs.pop('end_time', None)

            task_repeat = cls(**kwargs)
            task_repeat.start_time = start_time
            task_repeat.end_time = end_time

            return task_repeat

    def to_json(self):
        """
        Convert to JSON representation.
        """
        encoded = super().to_json()

        encoded['repeat'] = self.repeat.to_json()
        return encoded

    @staticmethod
    def json_to_dict(d: dict):
        """
        Convert the JSON representation of a repeatable task to an
        object dictionary decoding strings for timemap.util.Datetime,
        timemap.util.Timedelta and RepeatableTask.TaskRepeat instances
        into corresponding instances.

        :param d: JSON dictionary representing the task
        """
        d = Task.json_to_dict(d)

        d['repeat'] = RepeatableTask.TaskRepeat.from_json(d.get('repeat',
                                                                False))

        return d

    @property
    def start_time(self):
        """
        Get or set the start time of the task.  This property means
        different things for repeating and non-repeating tasks:
        - For non-repeating tasks, this property represents when the
          one iteration of the task starts.
        - For repeating tasks, this property represents when the
          first period of the task starts.
        """
        if self.repeat:
            return self.repeat.start_time
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        if self.repeat:
            self.repeat.start_time = start_time
            self._start_time = None
        else:
            self._start_time = start_time

    @start_time.deleter
    def start_time(self):
        if self.repeat:
            del self.repeat.start_time
        else:
            del self._start_time

    @property
    def end_time(self):
        """
        Get or set the end time of the task.  This property means
        different things for repeating and non-repeating tasks:
        - For non-repeating tasks, this property represents when the
          one iteration of the task ends.
        - For repeating tasks, this property represents when the
          time after which no periods start.
        """
        if self.repeat:
            return self.repeat.end_time
        return self._end_time

    @end_time.setter
    def end_time(self, end_time):
        if self.repeat:
            self.repeat.end_time = end_time
            self._end_time = None
        else:
            self._end_time = end_time

    @end_time.deleter
    def end_time(self):
        if self.repeat:
            del self.repeat.end_time
        else:
            del self._end_time

    def complete(self):
        """
        Complete the task.
        """
        # self.completed = True
        pass


class Event(RepeatableTask):
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
                 repeat: Event.EventRepeat=False,
                 partial_completion: bool=False,
                 max_divisions: int=-1,
                 thread_name: str=None):
        """
        :param name: the name of the event
        :param start_time: the start time of the event
        :param end_time: the end time of the event
        :param importance: the importance given to the task
        :param repeat: whether the task is repeating
        :param partial_completion: whether partial completion is useful
        :param max_divisions: the maximum number of non-consecutive
            time chunks that the task can be divided into
        :param thread_name: the name of the thread to which this task
            belongs
        """
        super().__init__(name, start_time, end_time, importance, repeat,
                         partial_completion, max_divisions, thread_name)

        self._appointments = None

    def __str__(self):
        """
        Return string representation of self,
        """
        return "Event: '{0.name}' in {0.start_time}-{0.end_time}".format(self)

    class EventRepeat(RepeatableTask.TaskRepeat):
        def __init__(self,
                     repeat: bool=False,
                     period: Timedelta=None):
            """
            :param repeat: whether the event is repeating
            :param period: the period of repetition
            """
            super().__init__(repeat, period)

            if self.repeat:
                self.appointments = []

        def to_json(self):
            """
            Convert to JSON representation.
            """
            encoded = super().to_json()

            if isinstance(encoded, bool):
                return encoded

            encoded['appointments'] = [appointment.to_json() for
                                       appointment in self.appointments]
            return encoded

        @staticmethod
        def json_to_dict(d: dict or bool):
            """
            Convert the JSON representation of an EventRepeat object to
            an object dictionary.

            :param d: JSON dictionary representing the EventRepeat
                object
            """
            d = super().json_to_dict(d)

            if isinstance(d, bool):
                return d

            d['assignments'] = [TimeChunk.from_json(assignment_json) for
                                assignment_json in d.get('assignments', [])]
            return d

    def to_json(self):
        """
        Convert to JSON representation.
        """
        encoded = super().to_json()

        encoded['type'] = 'event'
        return encoded

    @staticmethod
    def json_to_dict(d: dict):
        """
        Convert the JSON representation of an event to an object
        dictionary decoding strings for timemap.util.Datetime,
        timemap.util.Timedelta and Event.EventRepeat instances into
        corresponding instances.

        :param d: JSON dictionary representing the task
        """
        d = Task.json_to_dict(d)

        d['repeat'] = Event.EventRepeat.from_json(d.get('repeat', False))

        return d

    @property
    def appointments(self):
        """
        Get appointments for the event.  This property is not settable.
        Appointments can be added and removed with the add_appointment
        and remove_appointment methods.
        """
        if self.repeat:
            return self.repeat.appointments
        return self._appointments

    def add_appointment(self, appointment: TimeChunk):
        """
        Add an appointment to this event.  If the event is repeating,
        the appointment should start within one period of the event
        start date.  These appointments are then replicated once every
        period starting from the start date and continuing till the end
        date has been reached.
        """
        if not self.start_time:
            raise Exception("Invalid appointment: task start time not set")

        # noinspection PyTypeChecker
        if self.repeat:
            if appointment.start_time > self.start_time + self.repeat.period:
                raise Exception("Invalid appointment: time not within period")

        self.appointments.append(appointment)

    def remove_appointment(self, appointment: TimeChunk):
        """
        Remove an appointment from this event.  Does nothing if the
        appointment had not been previously added to the event.
        """
        if appointment in self.appointments:
            self.appointments.remove(appointment)


class Assignment(RepeatableTask):
    """
    Represents an assignment with a time deadline.  This type of task
    represents a dynamic task ie. one which can be moved around within
    well-defined ranges, usually now and the deadline.
    """

    def __init__(self,
                 name: str,
                 expected_duration: Timedelta=None,
                 importance: float=5,
                 repeat: Assignment.AssignmentRepeat=False,
                 partial_completion: bool=False,
                 max_divisions: int=-1,
                 thread_name: str=None):
        """
        :param name: the name of the event
        :param expected_duration: the expected time required to
            complete the assignment
        :param importance: the importance given to the task
        :param repeat: whether the task is repeating
        :param partial_completion: whether partial completion is useful
        :param max_divisions: the maximum number of non-consecutive
            time chunks that the task can be divided into
        :param thread_name: the name of the thread to which this task
            belongs
        """
        super().__init__(name,
                         importance=importance,
                         repeat=repeat,
                         partial_completion=partial_completion,
                         max_divisions=max_divisions,
                         thread_name=thread_name)

        self._deadlines = []
        self.expected_duration = expected_duration

    def __str__(self):
        """
        Return string representation of self,
        """
        return "Assignment: '{0.name}' by {0.deadline}".format(self)

    class AssignmentRepeat(RepeatableTask.TaskRepeat):
        def __init__(self,
                     repeat: bool=False,
                     period: Timedelta=None):
            super().__init__(repeat, period)

            if self.repeat:
                self.deadlines = []

        def to_json(self):
            """
            Convert to JSON representation. `
            """
            encoded = super().to_json()

            if isinstance(encoded, bool):
                return encoded

            encoded['deadlines'] = [deadline.to_json() for
                                    deadline in self.deadlines]
            return encoded

        @staticmethod
        def json_to_dict(d: dict or bool):
            """
            Convert the JSON representation of an AssignmentRepeat
            object to an object dictionary.

            :param d: JSON dictionary representing the AssignmentRepeat
                object
            """
            d = super().json_to_dict(d)

            if isinstance(d, bool):
                return d

            d['deadlines'] = [Datetime.from_json(deadline_json) for
                              deadline_json in d.get('deadlines', [])]
            return d

    def to_json(self):
        """
        Convert to JSON representation.
        """
        encoded = super().to_json()

        encoded['expected_duration'] = self.expected_duration.to_json()
        encoded['type'] = 'assignment'

        return encoded

    @staticmethod
    def json_to_dict(d: dict):
        """
        Convert the JSON representation of an assignment to an object
        dictionary decoding strings for timemap.util.Datetime,
        timemap.util.Timedelta and Assignment.AssignmentRepeat
        instances into corresponding instances.

        :param d: JSON dictionary representing the task
        """
        d = Task.json_to_dict(d)

        d['repeat'] = Assignment.AssignmentRepeat.from_json(d.get('repeat',
                                                                  False))
        d['expected_duration'] = Timedelta.from_json(d.get('expected_duration',
                                                           None))

        return d

    @property
    def deadlines(self):
        """
        Get deadlines for the event.  This property is not settable.
        Deadlines can be added and removed with the add_deadline and
        remove_deadline methods.
        """
        if self.repeat:
            return self.repeat.deadlines
        return self._deadlines

    def add_deadline(self, deadline: Datetime):
        """
        Add a deadline to this assignment.  If the assignment is
        repeating, the deadline should be within one period of the
        assignment start date.  These deadlines are then replicated
        once every period starting from the start date and continuing
        till the end date has been reached.
        """
        if not self.start_time:
            raise Exception("Invalid deadline: task start time not set")

        # noinspection PyTypeChecker
        if self.repeat:
            if deadline > self.start_time + self.repeat.period:
                raise Exception("Invalid deadline: time not within period")

        self.deadlines.append(deadline)

    def remove_deadline(self, deadline: Datetime):
        """
        Remove a deadline from this assignment.  Does nothing if the
        deadline had not been previously added to the assignment.
        """
        if deadline in self.deadlines:
            self.deadlines.remove(deadline)

    def is_done(self):
        """
        Return if the assignment is done.  A task is done if it has
        been completed or if its deadline is in the past.
        """
        if self.end_time:
            if self.end_time < Datetime.now(self.end_time.tzinfo):
                return True

        return self.completed
