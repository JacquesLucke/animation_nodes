from unittest import TestCase
from . polygon_indices_list import PolygonIndicesList

class TestAppend(TestCase):
    def setUp(self):
        self.list = PolygonIndicesList()

    def testNormal(self):
        self.list.append((1, 2, 3))
        self.list.append((4, 5, 6, 7))
        self.list.append((7, 5, 3))
        self.assertEquals(self.list[0], (1, 2, 3))
        self.assertEquals(self.list[1], (4, 5, 6, 7))
        self.assertEquals(self.list[2], (7, 5, 3))

class TestCopy(TestCase):
    def testNormal(self):
        self.list = PolygonIndicesList.fromValues([(1, 2, 3), (4, 5, 6, 7)])
        copy = self.list.copy()
        self.assertEquals(len(copy), 2)
        self.assertEquals(copy[0], (1, 2, 3))
        self.assertEquals(copy[1], (4, 5, 6, 7))
