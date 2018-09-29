import sys
from threading import Thread, Lock
from typing import Callable, Iterable
from warnings import warn
import pandas as pd
import numpy as np
import multiprocessing
import traceback


class StoppableThread(Thread):
    def __init__(self, fun: Callable, items: Iterable, callback: Callable = None, callback_each: int = 1):
        super().__init__()
        self.callback = callback
        self.callback_each = callback_each
        self.fun = fun
        self.items = items
        self.running = False
        self.current_index = 0
        self.results = []

    def run(self):
        self.running = True
        self.results = []
        for self.current_index, item in enumerate(self.items):
            if not self.running:
                break
            try:
                self.results.append(self.fun(item))
            except Exception:
                self.results.append(None)
                warn("Exception %s processing element %s" % (repr(sys.exc_info()[1]), str(item)))
            if self.callback is not None:
                if self.current_index % self.callback_each == 0:
                    self.callback()
        self.running = False


def parallelize(items: Iterable, fun: Callable, thread_count: int = None, progressbar: bool = True,
                progressbar_tick: int = 1):
    """
    This function iterates (in multithreaded fashion) over `items` and calls `fun` for each item.
    :param progressbar_tick:
    :param progressbar:
    :param items:
    :param fun:
    :param thread_count:
    :return:
    """

    if thread_count is None:
        thread_count = multiprocessing.cpu_count()

    lock = Lock()

    def _progressbar_callback():
        def report():
            lock.acquire()
            progress = [(t.current_index + 1) / len(t.items) if len(t.items) > 0 else 1.0 for t in threads]
            message = ["{0: <8.2%}".format(x) for x in progress]
            print(" ".join(message), end="\r", file=sys.stderr, flush=True)
            lock.release()

        return report

    items_split = np.array_split(items, thread_count)
    if progressbar:
        callback = _progressbar_callback()
    else:
        callback = None
    threads = [StoppableThread(fun, x, callback, progressbar_tick) for x in items_split]
    for t in threads:
        t.start()
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("Interrupting threads...")
        for t in threads:
            t.running = False
        for t in threads:
            t.join()
    if callback is not None:
        callback()
    collected_results = [item for thread in threads for item in thread.results]

    if isinstance(items, pd.Series):
        return pd.Series(list(collected_results), index=items.index)
    else:
        return collected_results
