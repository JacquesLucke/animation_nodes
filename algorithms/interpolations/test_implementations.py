from unittest import TestCase
from . implementations import (Linear,
                               PowerIn, PowerOut, PowerInOut,
                               ExponentialIn, ExponentialOut, ExponentialInOut)

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

class TestExponential(TestCase):
    def testExponentialIn(self):
        f = ExponentialIn(base = 3, exponent = 4)
        self.assertAlmostEqual(f(0.00), 0)
        self.assertAlmostEqual(f(0.25), 0.025)
        self.assertAlmostEqual(f(0.50), 0.1)
        self.assertAlmostEqual(f(0.75), 0.325)
        self.assertAlmostEqual(f(1.00), 1)

    def testExponentialOut(self):
        f = ExponentialIn(base = 2, exponent = 3)
        self.assertAlmostEqual(f(0.00), 0)
        self.assertAlmostEqual(f(0.25), 0.097399)
        self.assertAlmostEqual(f(0.50), 0.2612039)
        self.assertAlmostEqual(f(0.75), 0.5366898)
        self.assertAlmostEqual(f(1.00), 1)

    def testExponentialInOut(self):
        f = ExponentialInOut(base = 3, exponent = 3)
        self.assertAlmostEqual(f(0.00), 0)
        self.assertAlmostEqual(f(0.25), 0.0806952)
        self.assertAlmostEqual(f(0.50), 0.5)
        self.assertAlmostEqual(f(0.75), 0.9193048)
        self.assertAlmostEqual(f(1.00), 1)
