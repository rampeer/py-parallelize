import multiprocessing
import os
import sys
from multiprocessing import Queue
from queue import Empty
from threading import Thread, Lock
from time import time
from typing import Callable, Iterable
from warnings import warn

import numpy as np
import pandas as pd

fork_available = hasattr(os, "fork")


class StoppableThread(Thread):
    def __init__(self, fun: Callable, items: Iterable,
                 callback: Callable = None, callback_each: int = 1,
                 continue_on_exception: bool = False, exception_impute=None, exception_callback: Callable = None):
        super().__init__()
        self.callback = callback
        self.callback_each = callback_each
        self.fun = fun
        self.items = items
        self.running = False
        self.current_index = 0
        self.results = []
        self.continue_on_exception = continue_on_exception
        self.exception_impute = exception_impute
        self.exception = None
        self.exception_callback = exception_callback

    def run(self):
        self.running = True
        self.results = []
        for self.current_index, item in enumerate(self.items):
            if not self.running:
                break
            try:
                self.results.append(self.fun(item))
            except Exception as e:
                if not self.continue_on_exception:
                    self.exception = e
                    self.exception_callback()
                    break
                self.results.append(self.exception_impute)
                warn("%s processing element %s" % (repr(sys.exc_info()[1]), str(item)))
            if self.callback is not None:
                if self.current_index % self.callback_each == 0:
                    self.callback()
        self.running = False


def parallelize(items: Iterable, fun: Callable, thread_count: int = None, progressbar: bool = True,
                progressbar_tick: int = 1, continue_on_exception: bool = True, exception_impute=None,
                display_eta: bool = True):
    """
    This function iterates (in multithreaded fashion) over `items` and calls `fun` for each item.
    :param items: items to process.
    :param fun: function to apply to each `items` element.
    :param progressbar: should progressbar be displayed?
    :param progressbar_tick: how often should we update progressbar?
    :param thread_count: how many threads should be allocated? If None, this parameter will be chosen automatically.
    :param continue_on_exception: if True, it will print warning if `fun` fails on some element, instead of halting
    :param exception_impute: which value should be put into output when `fun` throws an exception?
    :param display_eta: Should an estimation of remaining time be displayed?
    """

    if thread_count is None:
        thread_count = multiprocessing.cpu_count()

    lock = Lock()

    def _progressbar_callback():
        def report():
            lock.acquire()
            total = int(sum([len(t.items) for t in threads]))
            current = int(sum([t.current_index + 1.0 if len(t.items) > 0 else 0 for t in threads]))

            if current > 0:
                eta = (time() - start_time) / current * (total - current)
            else:
                eta = 0
            message = "[{0: <40}] {1} / {2} ({3: .2%})".format(
                "#" * int(current / total * 40),
                current,
                total,
                current / total)
            if display_eta:
                message += " (ETA: {0}s)      ".format(round(eta))
            print(message, end="\r", file=sys.stderr, flush=True)
            lock.release()

        return report

    def _stop_all_threads():
        for t in threads:
            t.running = False

    items_split = np.array_split(items, thread_count)
    if progressbar:
        callback = _progressbar_callback()
    else:
        callback = None
    threads = [StoppableThread(fun, x,
                               callback, progressbar_tick,
                               continue_on_exception, exception_impute, _stop_all_threads) for x in items_split]
    start_time = time()
    for t in threads:
        t.start()
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("Interrupting threads...")
        _stop_all_threads()
        # We have to wait for all threads to process their current elements
        for t in threads:
            t.join()
    if callback is not None:
        callback()
        print("\n")

    # Any exceptions?
    for t in threads:
        if t.exception is not None:
            raise t.exception

    collected_results = [item for thread in threads for item in thread.results]

    if isinstance(items, pd.Series):
        return pd.Series(list(collected_results), index=items.index)
    else:
        return collected_results


def pfor(items: Iterable, process_count: int = None, progressbar: bool = True,
         progressbar_tick: int = 1, i_know_what_im_doing: bool = False) -> Iterable:
    """
    This function is supposed to be used in conjunction with `for`. It effectively executes `for` body in multithreaded
    fashion:
    ```
    for x in pfor(range(10)):
        # Something useful. It will be executed in parallel.
        pass
    ```
    :param items: Iterate over what?
    :param progressbar: should progressbar be displayed?
    :param progressbar_tick: how often should we update progressbar?
    :param process_count: how many processes should be allocated? If None, this parameter will be chosen automatically.
    :param i_know_what_im_doing: use of this function required `for` body to use `multithreading.Manager`'s lists and
    dicts because they are shared across processes:
    ```
    from multithreading import Manager
    with Manager() as m:
        l = m.list()
    ```
    tick this flag if you already did that. Otherwise, a warning will be displayed.
    """
    if not fork_available:
        raise Exception("No os.fork function available. Probably, you are using Windows, that does not support it.\n"
                        "Please use `parallelize` instead (or switch to other OS ;)")
    if process_count is None:
        process_count = multiprocessing.cpu_count()
    if not i_know_what_im_doing:
        warn("Please note that processes do not share memory.\n"
             "Therefore, you have to use multiprocessing lists and dicts\n"
             "as they are shared across processes:\n\n"
             "from multiprocessing import Manager\n"
             "with Manager() as m:\n"
             "\tl = m.list()\n"
             "\tfor x in pfor(range(10)):"
             "\t\tl.append(x ** 2)"
             "\tprint(l)\n\n")

    lock = Lock()

    q = Queue()
    item_count = 0
    for i in items:
        item_count += 1
        q.put(i)

    def report():
        lock.acquire()
        current = item_count - q.qsize()
        message = "[{0: <40}] {1} / {2} ({3: .2%})".format(
            "#" * int(current / item_count * 40),
            current,
            item_count,
            current / item_count)
        print(message, end="\r", file=sys.stderr, flush=True)
        lock.release()

    pids = []

    def _stop_all_processes():
        for pid in pids:
            os.kill(pid, 9)

    try:
        report()
        for _ in range(process_count):
            pid = os.fork()
            if pid == 0:
                try:
                    ticks = 0
                    while True:
                        ticks += 1
                        item = q.get(block=False)
                        yield item
                        if progressbar:
                            if ticks % progressbar_tick == 0:
                                report()
                except GeneratorExit:
                    lock.acquire()
                    print(
                        "An exception occured when processing element < %s >                           " % (str(item)))
                    print("Unfortunately, exception cannot be printed because                            ")
                    print("processes die on stumbling upon exception, and there is no way to recover it. ")
                    lock.release()
                    break
                except Empty:
                    pass
                finally:
                    os._exit(0)
            else:
                pids.append(pid)

        for pid in pids:
            os.waitpid(pid, 0)
        report()
    except KeyboardInterrupt:
        print("Interrupting threads...")
        _stop_all_processes()
        for pid in pids:
            os.waitpid(pid, 0)
        q = Queue()
    finally:
        print("\n")
        if not q.empty():
            print("Element queue is not empty. Apparently, all processes died. Probably, something is wrong "
                  "with your data or code.")
