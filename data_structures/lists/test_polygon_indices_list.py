from unittest import TestCase
from . base_lists import ULongList
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

    def testTooShort(self):
        with self.assertRaises(TypeError):
            self.list.append((3, 5))

    def testWrongType(self):
        with self.assertRaises(TypeError):
            self.list.append((4, "abc", 3))

    def testNegativeNumbers(self):
        with self.assertRaises(TypeError):
            self.list.append((4, -3, 6))

class TestCopy(TestCase):
    def testNormal(self):
        self.list = PolygonIndicesList.fromValues([(1, 2, 3), (4, 5, 6, 7)])
        copy = self.list.copy()
        self.assertEquals(len(copy), 2)
        self.assertEquals(copy[0], (1, 2, 3))
        self.assertEquals(copy[1], (4, 5, 6, 7))

class TestReversed(TestCase):
    def testNormal(self):
        self.list = PolygonIndicesList.fromValues([
            (1, 2, 3), (4, 5, 6, 7), (8, 9, 0)])
        newList = self.list.reversed()
        self.assertEquals(newList[0], (8, 9, 0))
        self.assertEquals(newList[1], (4, 5, 6, 7))
        self.assertEquals(newList[2], (1, 2, 3))

class TestJoin(TestCase):
    def testNormal(self):
        l1 = PolygonIndicesList.fromValues([(1, 2, 3), (4, 5, 6, 7)])
        l2 = PolygonIndicesList.fromValues([(2, 4, 7, 8), (1, 2, 3, 4)])
        l3 = PolygonIndicesList.fromValues([(6, 5, 4), (2, 3, 4, 5, 6)])
        newList = PolygonIndicesList.join(l1, l2, l3)
        self.assertEquals(len(newList), 6)
        self.assertEquals(newList[0], (1, 2, 3))
        self.assertEquals(newList[3], (1, 2, 3, 4))
        self.assertEquals(newList[5], (2, 3, 4, 5, 6))

class TestCopyWithNewOrder(TestCase):
    def setUp(self):
        self.list = PolygonIndicesList.fromValues([
            (1, 2, 3), (4, 5, 6, 7), (8, 9, 0)])

    def testNormal(self):
        order = ULongList.fromValues([1, 2, 0, 1])
        newList = self.list.copyWithNewOrder(order)
        self.assertEquals(len(newList), 4)
        self.assertEquals(newList[0], (4, 5, 6, 7))
        self.assertEquals(newList[1], (8, 9, 0))
        self.assertEquals(newList[2], (1, 2, 3))
        self.assertEquals(newList[3], (4, 5, 6, 7))

    def testEmptyList(self):
        myList = PolygonIndicesList()
        order = ULongList.fromValues([1])
        with self.assertRaises(IndexError):
            newList = myList.copyWithNewOrder(order)

    def testTooHighIndex(self):
        order = ULongList.fromValues([1, 0, 4, 2])
        with self.assertRaises(IndexError):
            newList = self.list.copyWithNewOrder(order)

class TestGetValuesInSlice(TestCase):
    def setUp(self):
        self.list = PolygonIndicesList.fromValues([
            (1, 2, 3), (4, 5, 6, 7), (8, 9, 0), (3, 4, 5),
            (5, 4, 2), (2, 7, 6), (3, 4, 6, 2, 8), (5, 3, 2)])

    def testStart(self):
        newList = self.list[:3]
        self.assertEquals(len(newList), 3)
        self.assertEquals(newList[0], (1, 2, 3))
        self.assertEquals(newList[1], (4, 5, 6, 7))
        self.assertEquals(newList[2], (8, 9, 0))

    def testEnd(self):
        newList = self.list[-3:]
        self.assertEquals(len(newList), 3)
        self.assertEquals(newList[0], (2, 7, 6))
        self.assertEquals(newList[1], (3, 4, 6, 2, 8))
        self.assertEquals(newList[2], (5, 3, 2))

    def testComplex(self):
        newList = self.list[2:-1:2]
        self.assertEquals(len(newList), 3)
        self.assertEquals(newList[0], (8, 9, 0))
        self.assertEquals(newList[1], (5, 4, 2))
        self.assertEquals(newList[2], (3, 4, 6, 2, 8))
