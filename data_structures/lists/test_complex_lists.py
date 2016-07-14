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

class TestJoin(TestCase):
    def testNormal(self):
        v1 = Vector3DList()
        v1.append((0, 0, 0))
        v1.append((1, 1, 1))
        v2 = Vector3DList()
        v2.append((2, 2, 2))
        v2.append((3, 3, 3))
        v3 = Vector3DList()
        v3.append((4, 4, 4))
        v3.append((5, 5, 5))

        result = Vector3DList.join(v1, v2, v3)
        self.assertEquals(len(result), 6)
        self.assertEquals(result[4], Vector((4, 4, 4)))

class TestAdd(TestCase):
    def testNormal(self):
        v1 = Vector3DList()
        v1.append((0, 0, 0))
        v1.append((1, 1, 1))
        v2 = Vector3DList()
        v2.append((2, 2, 2))
        v2.append((3, 3, 3))

        result = v1 + v2
        self.assertEquals(len(result), 4)
        self.assertEquals(result[2], Vector((2, 2, 2)))

class TestMultiply(TestCase):
    def testNormal(self):
        v = Vector3DList()
        v.append((0, 0, 0))
        v.append((1, 1, 1))
        r = v * 3
        self.assertEquals(len(r), 6)
        self.assertEquals(r[4], Vector((0, 0, 0)))

class TestInplaceAdd(TestCase):
    def testNormal(self):
        v1 = Vector3DList()
        v1.append((0, 0, 0))
        v1.append((1, 1, 1))
        v2 = Vector3DList()
        v2.append((2, 2, 2))
        v2.append((3, 3, 3))

        v1 += v2
        self.assertEquals(len(v1), 4)
        self.assertEquals(v1[2], Vector((2, 2, 2)))

class TestReversed(TestCase):
    def testNormal(self):
        v = Vector3DList()
        for i in range(4):
            v.append((i, i, i))
        r = v.reversed()
        self.assertEquals(r[0], Vector((3, 3, 3)))
        self.assertEquals(r[1], Vector((2, 2, 2)))
        self.assertEquals(r[2], Vector((1, 1, 1)))
        self.assertEquals(r[3], Vector((0, 0, 0)))
