#!/usr/bin/env python3

from threads.task import *


__author__ = "Dibyo Majumdar"
__email__ = "dibyo.majumdar@gmail.com"

__all__ = ["Thread"]


class ThreadException(Exception):
    pass


class Thread(object):
    """
    Represents one thread of life.  A thread contains a series of tasks
    that define it.  It is used to provide a level of organization to
    the tasks and for setting their relative importance.
    """
    def __init__(self,
                 name: str,
                 default_importance: int):
        """
        :param name: the name of the thread
        :param default_importance: the importance given by default to
            its tasks
        """
        self.name = name
        self.default_importance = default_importance
        self.tasks = []

    def __or__(self, other: Thread):
        """
        Return the union of this thread and other

        :param other: the other thread
        """
        if not isinstance(other, Thread):
            message = "unsupported operand type(s) for |: 'thread' and '{}'". \
                format(type(other))
            raise TypeError(message)

        new_thread = Thread(self.name, self.default_importance)
        new_thread.tasks = self.tasks

        new_thread |= other
        return new_thread

    def __ior__(self, other: Thread):
        """
        Execute the in-place union operation of this thread with other

        :param other: the other thread
        """
        if not isinstance(other, Thread):
            message = "unsupported operand type(s) for |=: 'thread' and '{}'".\
                format(type(other))
            raise TypeError(message)
        if self.name != other.name:
            raise TypeError("cannot find union: threads are not the same")

        tasks = set(self.tasks)
        tasks |= set(other.tasks)

        self.tasks = list(tasks)

    def to_json(self):
        """
        Convert to JSON representation
        """
        tasks = []
        for task in self.tasks:
            tasks.append(task.to_json())

        return {
            'name': self.name,
            'default_importance': self.default_importance,
            'tasks': tasks
        }

    @classmethod
    def from_json(cls, d: dict):
        """
        Create a Thread instance from its JSON representation

        :param d: JSON dictionary for the thread
        """
        thread = Thread(d['name'], d['default_importance'])

        for task_json in d.get('tasks', []):
            typ = task_json.get('type', None)
            if typ == 'event':
                thread.add_task(Event.from_json(task_json))
            elif typ == 'assignment':
                thread.add_task(Assignment.from_json(task_json))
            else:
                thread.add_task(Task.from_json(task_json))

        return thread

    def add_task(self,
                 task: Task):
        self.tasks.append(task)

    def create_task(self):
        pass