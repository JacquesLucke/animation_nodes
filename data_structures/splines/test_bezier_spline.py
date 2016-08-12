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

class TestGetTrimmedCopy(TestCase):
    def testSingleSegmentNormal(self):
        spline = self.getSingleSegmentSpline()
        newSpline = spline.getTrimmedCopy(0.2, 0.9)
        self.assertEqual(len(newSpline.points), 2)
        testEqual(self, newSpline.points[0], (-0.592, 0.392, 0.096))
        testEqual(self, newSpline.points[1], (1.6865, 1.2285, 0.243))
        testEqual(self, newSpline.rightHandles[0], (-0.004, 0.924, 0.292))
        testEqual(self, newSpline.leftHandles[1], (0.927, 1.603, 0.684))

    def testSingleSegmentFull(self):
        spline = self.getSingleSegmentSpline()
        newSpline = spline.getTrimmedCopy(0.0, 1.0)
        self.assertEqual(len(newSpline.points), 2)
        testEqual(self, newSpline.points[0], (-1, 0, 0))
        testEqual(self, newSpline.points[1], (2, 1, 0))
        testEqual(self, newSpline.rightHandles[0], (-0.5, 0.5, 0))
        testEqual(self, newSpline.leftHandles[1], (1, 2, 1))

    def testSingleSegmentSameParameter(self):
        spline = self.getSingleSegmentSpline()
        newSpline = spline.getTrimmedCopy(0.3, 0.3)
        self.assertTrue(len(newSpline.points) >= 1)
        for point in newSpline.points + newSpline.leftHandles + newSpline.rightHandles:
            testEqual(self, point, (-0.3205, 0.6255, 0.189))

    def testSingleSegmentBothParametersZero(self):
        spline = self.getSingleSegmentSpline()
        newSpline = spline.getTrimmedCopy(0, 0)
        self.assertTrue(len(newSpline.points) >= 1)
        for point in newSpline.points + newSpline.leftHandles + newSpline.rightHandles:
            testEqual(self, point, (-1, 0, 0))

    def testGetSingleSegmentFromMultipleSegments(self):
        spline = self.getMultiSegmentSpline()
        newSpline = spline.getTrimmedCopy(0.7, 0.9)
        self.assertEqual(len(newSpline.points), 2)
        testEqual(self, newSpline.points[0], (1.188, -1.272, -0.944))
        testEqual(self, newSpline.points[1], (-0.036, -2.316, 0.568))
        testEqual(self, newSpline.rightHandles[0], (1.356, -1.764, -0.728))
        testEqual(self, newSpline.leftHandles[1], (0.372, -1.968, 0.064))

    def testGetSingleSegmentOfCyclicSpline(self):
        spline = self.getMultiSegmentSpline()
        spline.cyclic = True
        newSpline = spline.getTrimmedCopy(0.8, 0.95)
        self.assertEqual(len(newSpline.points), 2)
        testEqual(self, newSpline.points[0], (0.232, -3.12, 0.896))
        testEqual(self, newSpline.points[1], (-0.992, -0.6, 0.104))
        testEqual(self, newSpline.rightHandles[0], (0.148, -2.82, 0.704))
        testEqual(self, newSpline.leftHandles[1], (-0.728, -1.44, 0.296))

    def getSingleSegmentSpline(self):
        spline = BezierSpline()
        spline.appendPoint((-1, 0, 0), (-1.5, -0.5, 0), (-0.5, 0.5, 0))
        spline.appendPoint((2, 1, 0), (1, 2, 1), (2, 0, 0))
        return spline

    def getMultiSegmentSpline(self):
        spline = BezierSpline()
        spline.appendPoint((-1, 0, 0), (-1.5, -0.5, 0), (-0.5, 0.5, 0))
        spline.appendPoint((2, 1, 0), (1, 2, 1), (2, 0, 0))
        spline.appendPoint((1, -1, -1), (0, 0, 0), (2, -2, -1))
        spline.appendPoint((0, -3, 1), (-1, -2, 1), (1, -4, 1))
        return spline

def testEqual(testCase, vector1, vector2):
    testCase.assertAlmostEqual(vector1[0], vector2[0], places = 5)
    testCase.assertAlmostEqual(vector1[1], vector2[1], places = 5)
    testCase.assertAlmostEqual(vector1[2], vector2[2], places = 5)
