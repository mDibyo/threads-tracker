#!/usr/bin/env python3

"""
This module contains classes representing different types of tasks.

Module structure:
- Task
  - Event
  - Assignment
  - RecurrentTask

"""
__author__ = 'dibyo'

from datetime import datetime, timedelta
import uuid
import json


class Task(object):
    """
    Represents a task.  This serves as the base class of all typed of
    tasks. It is also the final representation of all tasks in the
    created schedule.
    """
    def __init__(self,
                 name: str,
                 start_time: datetime=None,
                 end_time: datetime=None,
                 importance: int=5,
                 repeating: bool=False,
                 period: timedelta=None,
                 partial_completion: bool=False,
                 max_divisions: int=-1):
        """
        :param name: the name of the task
        :param start_time: the start time of the task
        :param end_time: the end time of the task
        :param importance: the importance given to the task
        :param repeating: whether the task is repeating
        :param period: the period of repetition of the task
        :param partial_completion: whether partial completion is useful
        :param max_divisions: the maximum number of non-consecutive timechunks
            that the task can be divided into
        """
        self.uid = uuid.uuid4()
        self.name = name
        self.start_time = self.end_time = None
        self._importance = importance
        self.repeating = repeating
        self.period = period
        self.partial_completion = partial_completion
        self.max_divisions = max_divisions

        if start_time:
            self.change_time(start_time, end_time)

    def __str__(self):
        """
        Return string representation of self.
        """
        return "Task {0.name} in {0.start_time}-{0.end_time}".format(self)

    class TaskJSONDecoder(json.JSONDecoder):
        pass

    class TaskJSONEncoder(json.JSONEncoder):
        pass

    def change_time(self,
                    new_start_time: datetime,
                    new_end_time: datetime=None):
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
    def importance(self, new_importance: int):
        """
        Change the importance of a task

        :param new_importance: the new importance of the task
        """
        if 0 <= new_importance < 10:
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
                 start_time: datetime,
                 end_time: datetime,
                 importance: int=5,
                 repeating: bool=False,
                 period: timedelta=None,
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
        :param max_divisions: the maximum number of non-consecutive timechunks
            that the task can be divided into
        """
        super(Event, self).__init__(name, start_time, end_time, importance,
                                    repeating, period, partial_completion,
                                    max_divisions)

    def __str__(self):
        """
        Return string representation of self,
        """
        return "Event {0.name} in {0.start_time}-{0.end_time}".format(self)


class Assignment(Task):
    """
    Represents an assignment with a time deadline.  This type of task
    represents a dynamic task ie. one which can be moved around within
    well-defined ranges, usually now and the deadline.
    """
    def __init__(self,
                 name: str,
                 deadline: datetime,
                 expected_duration: timedelta,
                 importance: int=5,
                 repeating: bool=False,
                 period: timedelta=None,
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
        :param max_divisions: the maximum number of non-consecutive timechunks
            that the task can be divided into
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
        return "Assignment {0.name} by {0.deadline}".format(self)

    def change_time(self,
                    new_start_time: datetime,
                    new_end_time: datetime=None):
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
