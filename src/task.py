__author__ = 'dibyo'

from datetime import time, timedelta

class Task(object):
    def __init__(self,
                 name: str):
        """
        :param name: the name of the task
        """
        self.name = name


class Event(Task):
    """
    Represents an event running between two fixed times.  This type of
    task represents a static task ie..one which can not be moved around
    in time.
    """
    def __init__(self,
                 name: str,
                 start_time: time,
                 end_time: time):
        """
        :param name: the name of the event
        :param start_time: the start time of the event
        :param end_time: the end time of the event
        """
        super(Event, self).__init__(name)
        self.start_time = start_time
        self.end_time = end_time


class Assignment(Task):
    """
    Represents an assignment with a time deadline.  This type of task
    represents a dynamic task ie. one which can be moved around within
    well-defined ranges, usually now and the deadline.
    """
    def __init__(self,
                 name: str,
                 deadline: time,
                 expected_duration: timedelta):
        """
        :param name: the name of the event
        :param deadline: the time at which the assignment is due
        :param expected_duration: the expected time required to
            complete the assignment
        """
        super(Assignment, self).__init__(name)
        self.deadline = deadline
        self.expected_duration = expected_duration