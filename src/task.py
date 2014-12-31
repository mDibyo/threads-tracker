__author__ = 'dibyo'

from datetime import datetime, timedelta


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
                 importance: int=5):
        """
        :param name: the name of the task
        :param start_time: the start time of the task
        :param end_time: the end time of the task
        """
        self.name = name
        self.start_time = self.end_time = None
        self.importance = importance

        if start_time:
            self.change_time(start_time, end_time)

    def __str__(self):
        """
        Return string representation of self.
        """
        return "Task {0.name} in {0.start_time}-{0.end_time}".format(self)

    def set_time(self,
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

    def set_importance(self, new_importance: int):
        """
        Change the importance of a task

        :param new_importance: the new importance of the task
        """
        if new_importance >= 0 and new_importance < 10:
            self.importance = new_importance
        else:
            raise Exception("Invalid importance for task. ")


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
                 importance: int=5):
        """
        :param name: the name of the event
        :param start_time: the start time of the event
        :param end_time: the end time of the event
        """
        super(Event, self).__init__(name, start_time, end_time, importance)

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
                 importance: int=5):
        """
        :param name: the name of the event
        :param deadline: the time at which the assignment is due
        :param expected_duration: the expected time required to
            complete the assignment
        """
        super(Assignment, self).__init__(name, importance=importance)
        self.deadline = deadline
        self.expected_duration = expected_duration

    def __str__(self):
        """
        Return string representation of self,
        """
        return "Assignment {0.name} by {0.deadline}".format(self)

    def set_time(self,
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
