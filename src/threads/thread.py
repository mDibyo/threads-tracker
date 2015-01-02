import json

from threads.task import Task


__author__ = "Dibyo Majumdar"
__email__ = "dibyo.majumdar@gmail.com"


class Thread(object):
    def __init__(self,
                 name: str,
                 default_importance: int):
        self.name = name
        self.default_importance = default_importance
        self.tasks = []

    class ThreadJSONEncoder(json.JSONEncoder):
        def default(self, o: Thread):
            tasks = []
            for task in o.tasks:
                Task.TaskJSONEncoder().encode(task)

    class ThreadJSONDecoder(json.JSONDecoder):
        pass

    def add_task(self,
                 task: Task):
        self.tasks.append(task)