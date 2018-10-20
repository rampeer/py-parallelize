import unittest
from multiprocessing import Manager
from pyparallelize.threaded import pfor


class MyTestCase(unittest.TestCase):
    def test_pfor(self):
        with Manager() as m:
            l = m.list()
            for x in pfor(range(10), i_know_what_im_doing=True):
                l.append(x ** 2)
            print(l)
            self.assertEqual(set(l), set([x**2 for x in range(10)]))

    def test_resilience(self):
        with Manager() as m:
            l = m.list()
            for x in pfor(range(10), i_know_what_im_doing=True):
                # An 1/0 exception will be thrown on first element.
                l.append(1 / x)
            print(l)
            self.assertEqual(set(l), set([1 / x for x in range(1, 10)]))


if __name__ == '__main__':
    unittest.main()
