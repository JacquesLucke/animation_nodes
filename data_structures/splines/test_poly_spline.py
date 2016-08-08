from mathutils import Vector
from unittest import TestCase
from . poly_spline import PolySpline

class TestInitialisation(TestCase):
    def testNormal(self):
        spline = PolySpline()
        self.assertFalse(spline.cyclic)
        self.assertEqual(spline.type, "POLY")
        self.assertEqual(len(spline.getPoints()), 0)

class TestAppendPoint(TestCase):
    def setUp(self):
        self.spline = PolySpline()

    def testNormal(self):
        self.spline.appendPoint((0, 0, 0))
        self.spline.appendPoint((1, 1, 1))
        points = self.spline.getPoints()
        self.assertEqual(len(points), 2)
        self.assertEqual(points[0], Vector((0, 0, 0)))
        self.assertEqual(points[1], Vector((1, 1, 1)))

    def testWrongType(self):
        with self.assertRaises(TypeError):
            self.spline.appendPoint("abc")

    def testTooLongVector(self):
        with self.assertRaises(TypeError):
            self.spline.appendPoint((0, 1, 2, 3))

class TestGetLength(TestCase):
    def testEmptySpline(self):
        spline = PolySpline()
        self.assertEqual(spline.getLength(), 0)

    def testSplineWithOnePoint(self):
        spline = PolySpline()
        spline.appendPoint((1, 2, 3))
        self.assertEqual(spline.getLength(), 0)

    def testSimple(self):
        spline = PolySpline()
        spline.appendPoint((0, 0, 0))
        spline.appendPoint((3, 4, 0))
        self.assertAlmostEqual(spline.getLength(), 5)

    def testMultiplePoints(self):
        spline = PolySpline()
        spline.appendPoint((0, 0, 0))
        spline.appendPoint((2, 4, 6))
        spline.appendPoint((2, 10, 8))
        self.assertAlmostEqual(spline.getLength(), 13.80787009)

    def testSimpleCyclic(self):
        spline = PolySpline()
        spline.cyclic = True
        spline.appendPoint((0, 0, 0))
        spline.appendPoint((3, 4, 0))
        self.assertAlmostEqual(spline.getLength(), 10)

    def testMultiplePointsCyclic(self):
        spline = PolySpline()
        spline.cyclic = True
        spline.appendPoint((0, 0, 0))
        spline.appendPoint((2, 4, 6))
        spline.appendPoint((2, 10, 8))
        self.assertAlmostEqual(spline.getLength(), 26.76935149)

class TestEvaluate(TestCase):
    def setUp(self):
        self.spline = PolySpline()
        self.spline.appendPoint((0, 0, 0))
        self.spline.appendPoint((2, 4, 6))
        self.spline.appendPoint((2, 10, 8))

    def testZero(self):
        testEqual(self, self.spline.evaluate(0), (0, 0, 0))

    def testOne(self):
        testEqual(self, self.spline.evaluate(1), (2, 10, 8))

    def testMiddle(self):
        testEqual(self, self.spline.evaluate(0.25), (1, 2, 3))
        testEqual(self, self.spline.evaluate(0.50), (2, 4, 6))
        testEqual(self, self.spline.evaluate(0.75), (2, 7, 7))

    def testWrongType(self):
        with self.assertRaises(TypeError):
            self.spline.evaluate("abc")

    def testInvalidValue(self):
        with self.assertRaises(ValueError):
            self.spline.evaluate(-1)
        with self.assertRaises(ValueError):
            self.spline.evaluate(1.5)

    def testEmptySpline(self):
        spline = PolySpline()
        with self.assertRaises(Exception):
            spline.evaluate(0)

    def testCyclic(self):
        self.spline.cyclic = True
        testEqual(self, self.spline.evaluate(0.0), (0, 0, 0))
        testEqual(self, self.spline.evaluate(1/3), (2, 4, 6))
        testEqual(self, self.spline.evaluate(0.5), (2, 7, 7))
        testEqual(self, self.spline.evaluate(2/3), (2, 10, 8))
        testEqual(self, self.spline.evaluate(5/6), (1, 5, 4))
        testEqual(self, self.spline.evaluate(1.0), (0, 0, 0))

class TestEvaluateTangent(TestCase):
    def setUp(self):
        self.spline = PolySpline()
        self.spline.appendPoint((0, 0, 0))
        self.spline.appendPoint((2, 4, 6))
        self.spline.appendPoint((2, 10, 8))

    def testZero(self):
        testEqual(self, self.spline.evaluateTangent(0), (2, 4, 6))

    def testOne(self):
        testEqual(self, self.spline.evaluateTangent(1), (0, 6, 2))

    def testMiddle(self):
        testEqual(self, self.spline.evaluateTangent(0.25), (2, 4, 6))
        testEqual(self, self.spline.evaluateTangent(0.50), (0, 6, 2))
        testEqual(self, self.spline.evaluateTangent(0.75), (0, 6, 2))

    def testWrongType(self):
        with self.assertRaises(TypeError):
            self.spline.evaluateTangent("abc")

    def testInvalidValue(self):
        with self.assertRaises(ValueError):
            self.spline.evaluateTangent(-1)
        with self.assertRaises(ValueError):
            self.spline.evaluateTangent(1.5)

    def testEmptySpline(self):
        spline = PolySpline()
        with self.assertRaises(Exception):
            spline.evaluateTangent(0)

    def testCyclic(self):
        self.spline.cyclic = True
        testEqual(self, self.spline.evaluateTangent(0.0), (2, 4, 6))
        testEqual(self, self.spline.evaluateTangent(0.1), (2, 4, 6))
        testEqual(self, self.spline.evaluateTangent(1/3), (0, 6, 2))
        testEqual(self, self.spline.evaluateTangent(0.5), (0, 6, 2))
        testEqual(self, self.spline.evaluateTangent(2/3), (-2, -10, -8))
        testEqual(self, self.spline.evaluateTangent(0.8), (-2, -10, -8))
        testEqual(self, self.spline.evaluateTangent(1.0), (-2, -10, -8))

def testEqual(testCase, vector1, vector2):
    testCase.assertAlmostEqual(vector1[0], vector2[0])
    testCase.assertAlmostEqual(vector1[1], vector2[1])
    testCase.assertAlmostEqual(vector1[2], vector2[2])
