__author__ = 'dibyo'

from thread.task import Task


class Thread(object):
    def __init__(self,
                 name: str,
                 default_importance: int):
        self.name = name
        self.default_importance = default_importance
        self.tasks = []

    def add_task(self,
                 task: Task):
        self.tasks.append(task)