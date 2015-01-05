#!/usr/bin/env python3


import os
import json

from threads.thread import Thread

__author__ = "Dibyo Majumdar"
__email__ = "dibyo.majumdar@gmail.com"


__all__ = [
    'TimeManager',
    'TaskManager'
]

# ROOT_DIRECTORY
ROOT_DIRECTORY = os.path.normpath(os.path.join(__file__, '../data'))


class TimeManager():
    """
    Stores and manages time.  This involves mapping time chunks to
    different tasks and loading and storing time mappings when the
    program is started or stopped respectively.

    Currently, time mappings are stored as JSON in files with the
    following directory and file structure:
    - ROOT_DIRECTORY/timemap/future/planned.json: stores time maps for
      times chunks in the future/present.
    - ROOT_DIRECTORY/timemap/past/planned.json: stores planned mappings
      of time chunks to tasks in the past.
    - ROOT_DIRECTORY/timemap/past/actual.json: stores actual mappings
      of time chunks to tasks in the past.
    """
    def __init__(self):
        pass

    def load(self):
        pass

    def save(self):
        pass


class TaskManager():
    """
    Store tasks and provide methods for managing their state.  This
    involves loading and saving them when the program is started and
    stopped respectively. This also involves basic determinations such
    as which tasks have been completed, which tasks have deadlines or
    start times that have passed and which are still left to do.

    Currently, task states are stored as JSON in files with the
    following directory and file structure:
    - ROOT_DIRECTORY/threads/future/{thread_name}.json: stores tasks
      belonging to thread with name {thread_name} which can be
      completed at a future/present time.
    - ROOT_DIRECTORY/threads/past/{thread_name}.json: stores tasks
      belonging to thread with name {thread_name} which should have
      been completed at a past time or has already been completed.
    """

    def __init__(self):
        self.threads = []
        self.tasks = {}

        self.dir_past = os.path.join(ROOT_DIRECTORY, 'threads', 'past')
        self.dir_future = os.path.join(ROOT_DIRECTORY, 'threads', 'future')

    def _filter_tasks(self):
        """
        Filter tasks in threads into past and future threads in
        preparation for a save and/or refresh of task states.

        :return : threads_past, threads_future
        :rtype: tuple
        """
        threads_past = []
        threads_future = []

        for thread in self.threads:
            thread_past = Thread(thread.name,
                                 thread.default_importance)
            thread_future = Thread(thread.name,
                                   thread.default_importance)

            for task in thread.tasks:
                if task.is_done():
                    thread_past.add_task(task)
                else:
                    thread_future.add_task(task)

            threads_past.append(threads_past)
            threads_future.append(threads_future)

        return threads_past, threads_future

    @staticmethod
    def _append_to_thread_file(file_path: str,
                               thread: Thread):
        """
        Append tasks in a thread to an existing thread on file

        :param file_path: the path to the thread file
        :param thread: the thread to be stored
        """
        with open(file_path, 'r+') as f:
            old_thread = Thread.from_json(json.load(f))
            old_thread |= thread

            f.seek(0)
            f.truncate()
            json.dump(old_thread.to_json(), f)

    @staticmethod
    def _overwrite_thread_file(file_path: str,
                               thread: Thread):
        """
        Write out thread on file overwriting if necessary

        :param file_path: the path to the thread file
        :param thread: the thread to be stored
        """
        with open(file_path, 'w') as f:
            json.dump(thread.to_json(), f)

    @staticmethod
    def _read_thread_file(file_path: str):
        """
        Read in thread from file

        :param file_path: the path to the thread file
        """
        with open(file_path, 'r') as f:
            return Thread.from_json(json.load(f))

    def save_state(self):
        """
        Save all tasks to file,  Tasks are encoded in JSON and stored
        in file according to scheme presented in the class description.
        """
        threads_past, threads_future = self._filter_tasks()

        for thread in threads_past:
            file_path = os.path.join(self.dir_past,
                                     "{0}.json".format(thread.name))
            self._append_to_thread_file(file_path, thread)

        for thread in threads_future:
            file_path = os.path.join(self.dir_future,
                                     "{0}.json".format(thread.name))
            self._overwrite_thread_file(file_path, thread)

    def load_state(self):
        """
        Load all tasks from file.  Tasks are encoded in JSON and stored
        in file according to scheme presented in the class description.
        """
        self.threads = []
        for thread_file in os.listdir(self.dir_future):
            thread = self._read_thread_file(os.path.join(self.dir_future,
                                                         thread_file))
            self.threads.append(thread)

    def refresh_state(self):
        """
        Refresh all tasks.  This involves saving them to file and
        loading them back in, in the process, getting rid of tasks that
        have been completed.
        """
        self.save_state()
        self.load_state()