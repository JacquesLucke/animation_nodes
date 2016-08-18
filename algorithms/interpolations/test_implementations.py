from unittest import TestCase
from . implementations import (Linear,
                               PowerIn, PowerOut, PowerInOut)

class TestLinear(TestCase):
    def testNormal(self):
        f = Linear()
        self.assertEqual(f(0.00), 0)
        self.assertEqual(f(0.25), 0.25)
        self.assertEqual(f(0.50), 0.5)
        self.assertEqual(f(0.75), 0.75)
        self.assertEqual(f(1.00), 1)

    def testBelowZero(self):
        f = Linear()
        self.assertEqual(f(-1), 0)

    def testAboveOne(self):
        f = Linear()
        self.assertEqual(f(2), 1)

class TestPower(TestCase):
    def testPowerOut(self):
        f = PowerOut(exponent = 2)
        self.assertEqual(f(0.00), 0)
        self.assertEqual(f(0.25), 0.4375)
        self.assertEqual(f(0.50), 0.75)
        self.assertEqual(f(0.75), 0.9375)
        self.assertEqual(f(1.00), 1)

    def testPowerIn(self):
        f = PowerIn(exponent = 3)
        self.assertEqual(f(0.00), 0)
        self.assertEqual(f(0.25), 0.015625)
        self.assertEqual(f(0.50), 0.125)
        self.assertEqual(f(0.75), 0.421875)
        self.assertEqual(f(1.00), 1)

    def testPowerInOut(self):
        f = PowerInOut(exponent = 2)
        self.assertEqual(f(0.00), 0)
        self.assertEqual(f(0.25), 0.125)
        self.assertEqual(f(0.50), 0.5)
        self.assertEqual(f(0.75), 0.875)
        self.assertEqual(f(1.00), 1)
