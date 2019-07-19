import multiprocessing
import unittest
from time import sleep, time

from pyparallelize import parallelize


class MyTestCase(unittest.TestCase):
    def test_something(self):
        x = [1, 2, 3, 4]
        y = parallelize(x, lambda x: x * x)
        self.assertEqual(y, [1, 4, 9, 16])

    def test_exceptions(self):
        x = [1, 2, 0, 5]

        def fun(x):
            if x == 0:
                raise ZeroDivisionError
            else:
                return 10 / x

        y = parallelize(x, fun)
        self.assertEqual(y, [10, 5, None, 2])

        try:
            y = parallelize(x, fun, continue_on_exception=False)
            self.assertTrue(False)
        except ZeroDivisionError:
            pass

        obj = object()
        y = parallelize(x, fun, exception_impute=obj)
        self.assertEqual(y[2], obj)

    def test_empty(self):
        e = parallelize([], lambda x: x)
        self.assertEqual(len(e), 0)

    def test_order(self):
        def fun(x):
            sleep(x)
            return x
        x = [0.5, 0.3, 0.2, 0.6, 0.4, 0.1, 0.5, 0.1, 0.2, 0.5, 0.6]
        y = parallelize(x, fun)
        self.assertEqual(x, y)

    def test_series(self):
        import pandas as pd
        x = pd.Series([1, 2, 3], index=["a", "b", "c"])
        y = parallelize(x, lambda p: p * 2)
        y_true = x.apply(lambda p: p * 2)
        self.assertTrue((y == y_true).all())
        self.assertTrue((y.index == y_true.index).all())

    def test_speed_increase(self):
        x = [0.1, 0.1, 0.1, 0.1]

        # Single-thread execution
        start = time()
        list([sleep(i) for i in x])
        duration_single = time() - start

        # Parallelized execution
        start = time()
        def fun(x):
            sleep(x)
            return x
        y = parallelize(x, fun)
        duration_multithreaded = time() - start

        if multiprocessing.cpu_count() > 1:
            # Strictly speaking, this might fail occasionally when
            # some heavy process starts eating CPU right after single-threaded variant is executed.
            self.assertLess(duration_multithreaded, duration_single)


if __name__ == '__main__':
    unittest.main()
