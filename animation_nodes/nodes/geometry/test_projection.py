from mathutils import Vector
from unittest import TestCase
from . c_utils import (
                       project_PointOnLine_Single,
                       project_PointOnPlane_Single)

class TestProject(TestCase):
    def testProjectOnLine(self):
        self.result = project_PointOnLine_Single(Vector((0, 0, 0)),
                                                 Vector((1, 0, 0)),
                                                 Vector((1, 1, 0)))
        self.assertEqual(self.result, (Vector((1, 0, 0)), 1, 1))

    def testProjectOnPlane(self):
        self.result = project_PointOnPlane_Single(Vector((0, 0, 0)),
                                                  Vector((0, 0, 1)),
                                                  Vector((0, 0, 1)))
        self.assertEqual(self.result, (Vector((0, 0, 0)), 1))
