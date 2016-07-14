from mathutils import Vector
from unittest import TestCase
from . complex_lists import Vector3DList

class TestInitialisation(TestCase):
    def testEmpty(self):
        v = Vector3DList()
        self.assertEquals(len(v), 0)

    def testWithLength(self):
        v = Vector3DList(10)
        self.assertEquals(len(v), 10)

    def testWithBoth(self):
        v = Vector3DList(10, 30)
        self.assertEquals(len(v), 10)

class TestAppend(TestCase):
    def testFirst(self):
        v = Vector3DList()
        v.append((1, 2, 3))
        self.assertEquals(len(v), 1)

    def testWrongInputLength(self):
        v = Vector3DList()
        with self.assertRaises(ValueError):
            v.append((2, 4))
        with self.assertRaises(ValueError):
            v.append((2, 4, 7, 9))

    def testWrongInputType(self):
        v = Vector3DList()
        with self.assertRaises(TypeError):
            v.append("abc")

class TestGetSingleItem(TestCase):
    def testEmptyList(self):
        v = Vector3DList()
        with self.assertRaises(IndexError):
            a = v[0]

    def testNormal(self):
        v = Vector3DList()
        for i in range(5):
            v.append((i, i, i))
        self.assertEquals(v[0], Vector((0, 0, 0)))
        self.assertEquals(v[1], Vector((1, 1, 1)))
        self.assertEquals(v[4], Vector((4, 4, 4)))

    def testNegativeIndex(self):
        v = Vector3DList()
        for i in range(5):
            v.append((i, i, i))
        self.assertEquals(v[-1], Vector((4, 4, 4)))
        self.assertEquals(v[-3], Vector((2, 2, 2)))
        with self.assertRaises(IndexError):
            a = v[-10]

    def testReturnType(self):
        v = Vector3DList()
        v.append((0, 0, 0))
        self.assertIsInstance(v[0], Vector)
