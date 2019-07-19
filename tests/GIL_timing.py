import unittest
from time import sleep, time

import numpy as np

from pyparallelize import parallelize


class MyTestCase(unittest.TestCase):
    @staticmethod
    def allocation_fun(x):
        return np.random.normal(x, 1.0, (1000, 1000)).sum()

    @staticmethod
    def pure_io_fun(x):
        return sleep(0.1)

    def mixed_fun(self, x):
        x = np.random.normal(0.0, 1e-5, (1000, 1000))
        for _ in range(10):
            x = np.multiply(x, x)

    def common_struct_fun(self, x):
        return np.add(self.a, self.b).sum()

    def time_that(self, N, fun):
        x = [0] * N

        # Parallelized execution
        start = time()
        parallelize(x, fun, progressbar=False)
        duration_multithreaded = time() - start
        print(f"Multi-threaded execuition: {duration_multithreaded} seconds")

        # Single-thread execution
        start = time()
        list([fun(i) for i in x])
        duration_single = time() - start
        print(f"Single-threaded execuition: {duration_single} seconds")

    def test_funcs(self):
        self.a = np.random.normal(0.0, 1.0, (30, 30))
        self.b = np.random.normal(0.0, 1.0, (30, 30))

        print("\nFunction that allocates memory and does some calculations")
        self.time_that(100, self.mixed_fun)

        print("\nFunction that use common struct")
        self.time_that(100000, self.common_struct_fun)

        print("\nFunction that spends time in I/O")
        self.time_that(50, self.pure_io_fun)

        print("\nFunction that just allocates memory")
        self.time_that(100, self.allocation_fun)


if __name__ == '__main__':
    unittest.main()
