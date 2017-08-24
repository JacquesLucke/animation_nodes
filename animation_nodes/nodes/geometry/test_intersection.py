from mathutils import Vector
from unittest import TestCase
from . c_utils import (
                       intersect_LineLine_Single,
                       intersect_LinePlane_Single,
                       intersect_LineSphere_Single,
                       intersect_PlanePlane_Single,
                       intersect_SpherePlane_Single,
                       intersect_SphereSphere_Single)

class TestLineLine(TestCase):
    def testValidLineLine(self):
        self.result = intersect_LineLine_Single(Vector((1, 1, 0)),
                                                Vector((-1, -1, 0)),
                                                Vector((1, -1, 0)),
                                                Vector((-1, 1, 0)))
        self.assertEqual(self.result, (Vector((0, 0, 0)),
                                       Vector((0, 0, 0)),
                                       0.5, 0.5, True))

    def testInvalidLineLine(self):
        self.result = intersect_LineLine_Single(Vector((1, 1, 0)),
                                                Vector((1, -1, 0)),
                                                Vector((-1, 1, 0)),
                                                Vector((-1, -1, 0)))
        self.assertEqual(self.result, (Vector((0, 0, 0)),
                                       Vector((0, 0, 0)),
                                       0, 0, False))

class TestLinePlane(TestCase):
    def testValidLinePlane(self):
        self.result = intersect_LinePlane_Single(Vector((0, 0, 1)),
                                                 Vector((0, 0, -1)),
                                                 Vector((0, 0, 0)),
                                                 Vector((0, 0, 1)))
        self.assertEqual(self.result, (Vector((0, 0, 0)), 0.5, True))

    def testInvalidLinePlane(self):
        self.result = intersect_LinePlane_Single(Vector((0, 0, 1)),
                                                 Vector((1, 0, 1)),
                                                 Vector((0, 0, 0)),
                                                 Vector((0, 0, 1)))
        self.assertEqual(self.result, (Vector((0, 0, 0)), 0, False))

class TestLineSphere(TestCase):
    def testLineSphereOneIntersection(self):
        self.result = intersect_LineSphere_Single(Vector((1, 0, 1)),
                                                  Vector((-1, 0, 1)),
                                                  Vector((0, 0, 0)), 1)
        self.assertEqual(self.result, (Vector((0, 0, 1)),
                                       Vector((0, 0, 1)),
                                       0.5, 0.5, 1))

    def testLineSphereTwoIntersections(self):
       self.result = intersect_LineSphere_Single(Vector((0, 0, 0)),
                                                 Vector((0, 0, 2)),
                                                 Vector((0, 0, 0)), 1)
       self.assertEqual(self.result, (Vector((0, 0, 1)),
                                      Vector((0, 0, -1)),
                                      0.5, -0.5, 2))

    def testInvalidLineSphere(self):
        self.result = intersect_LineSphere_Single(Vector((2, 0, -1)),
                                                  Vector((2, 0, 1)),
                                                  Vector((0, 0, 0)), 1)
        self.assertEqual(self.result, (Vector((0, 0, 0)),
                                       Vector((0, 0, 0)),
                                       0, 0, 0))

class TestPlanePlane(TestCase):
    def testValidPlanePlane(self):
        self.result = intersect_PlanePlane_Single(Vector((0, 0, 0)),
                                                  Vector((0, 0, 1)),
                                                  Vector((0, 0, 0)),
                                                  Vector((1, 0, 0)))
        self.assertEqual(self.result, (Vector((0, 1, 0)), Vector((0, 0, 0)), True))

    def testInvalidPlanePlane(self):
        self.result = intersect_PlanePlane_Single(Vector((0, 0, 0)),
                                                  Vector((0, 0, 1)),
                                                  Vector((0, 0, 1)),
                                                  Vector((0, 0, 1)))
        self.assertEqual(self.result, (Vector((0, 0, 0)), Vector((0, 0, 0)), False))

class TestSpherePlane(TestCase):
    def testValidSpherePlane(self):
        self.result = intersect_SpherePlane_Single(Vector((0, 0, 0)), 1,
                                                   Vector((0, 0, 0)),
                                                   Vector((0, 0, 1)))
        self.assertEqual(self.result, (Vector((0, 0, 0)), 1, True))

    def testInvalidSpherePlane(self):
        self.result = intersect_SpherePlane_Single(Vector((0, 0, 0)), 1,
                                                   Vector((0, 0, 9)),
                                                   Vector((0, 0, 1)))
        self.assertEqual(self.result, (Vector((0, 0, 0)), 0, False))

class TestSphereSphere(TestCase):
    def testValidSphereSphere(self):
        self.result = intersect_SphereSphere_Single(Vector((0, 0, -1)), 1,
                                                    Vector((0, 0, 1)), 1)
        self.assertEqual(self.result, (Vector((0, 0, 0)), Vector((0, 0, 2)), 0, True))

    def testInvalidSphereSphere(self):
        self.result = intersect_SphereSphere_Single(Vector((0, 0, -2)), 1,
                                                    Vector((0, 0, 2)), 1)
        self.assertEqual(self.result, (Vector((0, 0, 0)), Vector((0, 0, 0)), 0, False))
