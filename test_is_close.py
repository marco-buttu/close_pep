#!/usr/bin/env python3

"""
Unit tests for is_close function
"""

import unittest
from decimal import Decimal
from fractions import Fraction
from is_close import is_close


class ErrorTestCase(unittest.TestCase):
    """
    Exceptions should be raised if either tolerance is set to less than zero
    """
    def test_negative_tol(self):
        with self.assertRaises(ValueError):
            is_close(1, 1, -1e-100)

    def test_negative_abstol(self):
        with self.assertRaises(ValueError):
            is_close(1, 1, 1e-100, -1e10)

    def test_bad_method(self):
        with self.assertRaises(ValueError):
            is_close(1.0001, 1.0002, method='week')


class CloseTestCase(unittest.TestCase):
    """ some methods that make it easier to test a bunch of values"""

    def do_close(self, a, b, *args, **kwargs):
        self.assertTrue(is_close(a, b, *args, **kwargs),
                        msg="%s and %s should be close!" % (a, b))

    def do_not_close(self, a, b, *args, **kwargs):
        self.assertFalse(is_close(a, b, *args, **kwargs),
                         msg="%s and %s should not be close!" % (a, b))

    def do_close_all(self, examples, *args, **kwargs):
        for method in ("asymmetric", "strong", "weak", "average"):
            for a, b in examples:
                kwargs['method'] = method
                self.assertTrue(is_close(a, b, *args, **kwargs),
                                msg=("%s and %s should be close with method:"
                                     " %s" % (a, b, method)))

    def do_not_close_all(self, examples, *args, **kwargs):
        for method in ("asymmetric", "strong", "weak", "average"):
            for a, b in examples:
                kwargs['method'] = method
                self.assertFalse(is_close(a, b, *args, **kwargs),
                                 msg=("%s and %s should not be close with"
                                      " method: %s" % (a, b, method)))


class ExactTestCase(CloseTestCase):
    """
    Make sure exact values test as close
    """
    exact_examples = [(2.0, 2.0),
                      (0.1e200, 0.1e200),
                      (1.123e-300, 1.123e-300),
                      (12345, 12345.0),
                      (0.0, -0.0),
                      (345678, 345678)
                      ]

    def test_exact(self):
        # should return close even with zero tolerances
        self.do_close_all(self.exact_examples,
                          rel_tol=0.0,
                          abs_tol=0.0)


class RelativeTestCase(CloseTestCase):

    nums8 = [(1e8, 1e8 + 1),
             (-1e-8, -1.00000001e-8),
             (1.12345678, 1.12345679),
             ]

    def test_all_8close(self):
        self.do_close_all(self.nums8, rel_tol=1e-8)

    def test_all_8_not_close(self):
        self.do_not_close_all(self.nums8, rel_tol=1e-9)


class ZeroTestCase(CloseTestCase):

    nums0 = [(1e-9, 0.0),
             (-1e-9, 0.0),
             (-1e-150, 0.0),
             ]

    def test_nums8_not_close(self):
        # these should not be close to any rel_tol
        self.do_not_close_all(self.nums0, rel_tol=1)

    def test_nums8_close(self):
        # these should be close to abs_tol=1e-8
        self.do_close_all(self.nums0, abs_tol=1e-8)


class NonFiniteCase(CloseTestCase):
    """ test for nan, inf, -inf """
    inf = float('inf')
    nan = float('nan')
    close_examples = [(inf, inf),
                      (-inf, -inf),
                      ]

    not_close_examples = [(nan, nan),
                          (nan, 1e-100),
                          (1e-100, nan),
                          (inf, nan),
                          (nan, inf),
                          (inf, -inf),
                          (inf, 1.0),
                          (1.0, inf),
                          ]

    def test_close(self):
        self.do_close_all(self.close_examples, abs_tol=1e12)  # huge!

    def test_not_close(self):
        self.do_not_close_all(self.not_close_examples, abs_tol=1e12)  # huge!


class AsymetryTest(CloseTestCase):
    """
    tests the assymetry example from the PEP
    """
    def test_close(self):
        self.do_close(9, 10, rel_tol=0.1, method='asymmetric')

    def test_not_close(self):
        self.do_not_close(10, 9, rel_tol=0.1, method='asymmetric')

    # should pass weak test both orders
    def test_close_weak(self):
        self.do_close(9, 10, rel_tol=0.1, method='weak')

    def test_close_weak_reversed(self):
        self.do_close(10, 9, rel_tol=0.1, method='weak')

    # should fail strong test both orders
    def test_not_close_strong(self):
        self.do_not_close(9, 10, rel_tol=0.1, method='strong')

    def test_not_close_strong_reversed(self):
        self.do_not_close(10, 9, rel_tol=0.1, method='strong')

    # should fail average test both ways
    def test_not_close_average(self):
        self.do_not_close(9, 10, rel_tol=0.1, method='average')

    def test_not_close_average_reversed(self):
        self.do_not_close(10, 9, rel_tol=0.1, method='average')


class ComplexTests(CloseTestCase):
    close_examples = [(1.0+1.0j, 1.000000000001+1.0j),
                      (1.0+1.0j, 1.0+1.000000000001j),
                      (-1.0+1.0j, -1.000000000001+1.0j),
                      (1.0-1.0j, 1.0-0.999999999999j),
                      ]

    def test_close(self):
        self.do_close_all(self.close_examples, rel_tol=1e-12)

        # for a,b in self.close_examples:
        #     self.do_close(a, b, rel_tol=1e-12)

    def test_not_close(self):
        self.do_not_close_all(self.close_examples, rel_tol=1e-13)
        # for a,b in self.close_examples:
        #     self.do_not_close(a, b, rel_tol=1e-14)


class TestInteger(CloseTestCase):
    close_examples = [(100000001, 100000000),
                      (123456789, 123456788)
                      ]

    def test_close(self):
        self.do_close_all(self.close_examples, rel_tol=1e-8)

    def test_not_close(self):
        self.do_not_close_all(self.close_examples, rel_tol=1e-9)


class TestDecimal(CloseTestCase):
    close_examples = [(Decimal('1.00000001'), Decimal('1.0')),
                      (Decimal('1.00000001e-20'), Decimal('1.0e-20')),
                      (Decimal('1.00000001e-100'), Decimal('1.0e-100')),
                      ]

    def test_close(self):
        self.do_close_all(self.close_examples, rel_tol=Decimal('1e-8'))

    def test_not_close(self):
        self.do_not_close_all(self.close_examples, rel_tol=Decimal('1e-9'))


class TestFraction(CloseTestCase):
    # could use some more here!
    close_examples = [(Fraction(1, 100000000) + 1, Fraction(1)),
                      ]

    def test_close(self):
        self.do_close_all(self.close_examples, rel_tol=1e-8)

    def test_not_close(self):
        self.do_not_close_all(self.close_examples, rel_tol=1e-9)

