from mathutils import Vector
from unittest import TestCase
from . bezier_spline import BezierSpline

class TestInitialisation(TestCase):
    def testNormal(self):
        spline = BezierSpline()
        self.assertFalse(spline.cyclic)
        self.assertEqual(spline.type, "BEZIER")

class TestEvaluate(TestCase):
    def setUp(self):
        self.spline = BezierSpline()
        self.spline.appendPoint((-1, 0, 0), (-1, 1, 0), (-1, -1, 0))
        self.spline.appendPoint((1, 0, 0), (1, 1, 0), (1, -1, 0))
        self.spline.appendPoint((0, -2, 0), (1, -2, 0), (-1, -2, 0))

    def testStart(self):
        testEqual(self, self.spline.evaluate(0), (-1, 0, 0))

    def testEnd(self):
        testEqual(self, self.spline.evaluate(1), (0, -2, 0))

    def testNormal(self):
        testEqual(self, self.spline.evaluate(0.25), (0, 0, 0))
        testEqual(self, self.spline.evaluate(0.5), (1, 0, 0))
        testEqual(self, self.spline.evaluate(0.75), (0.875, -1.375, 0))

class TestEvaluateTangent(TestCase):
    def setUp(self):
        self.spline = BezierSpline()
        self.spline.appendPoint((-1, 0, 0), (-1, 1, 0), (-1, -1, 0))
        self.spline.appendPoint((1, 0, 0), (1, 1, 0), (1, -1, 0))
        self.spline.appendPoint((0, -2, 0), (1, -2, 0), (-1, -2, 0))

    def testStart(self):
        testEqual(self, self.spline.evaluateTangent(0), (0, -3, 0))

    def testEnd(self):
        testEqual(self, self.spline.evaluateTangent(1), (-3, 0, 0))

    def testNormal(self):
        testEqual(self, self.spline.evaluateTangent(0.25), (3, 1.5, 0))
        testEqual(self, self.spline.evaluateTangent(0.5), (0, -3, 0))
        testEqual(self, self.spline.evaluateTangent(0.75), (-0.75, -2.25, 0))

def testEqual(testCase, vector1, vector2):
    testCase.assertAlmostEqual(vector1[0], vector2[0], places = 5)
    testCase.assertAlmostEqual(vector1[1], vector2[1], places = 5)
    testCase.assertAlmostEqual(vector1[2], vector2[2], places = 5)
