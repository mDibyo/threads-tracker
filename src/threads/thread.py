from threads.task import *


__author__ = "Dibyo Majumdar"
__email__ = "dibyo.majumdar@gmail.com"


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