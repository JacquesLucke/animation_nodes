from libc.limits cimport INT_MAX
from ... sockets.info import getSocketClass
from ... data_structures cimport CList, PolygonIndicesList

def getFillFunction(str dataType):
    socketClass = getSocketClass(dataType)
    defaultValue = socketClass.getDefaultValue()

    if isinstance(defaultValue, list):
        return fill_PythonList_NoCopy
    elif isinstance(defaultValue, CList):
        return fill_CList
    elif isinstance(defaultValue, PolygonIndicesList):
        raise NotImplementedError()
    else:
        raise NotImplementedError()

def fillList(str dataType, myList, str direction, length, element):
    length = min(max(length, 0), INT_MAX)
    return getFillFunction(dataType)(myList, direction, length, element)

def fill_PythonList_NoCopy(list myList, str direction, int length, element):
    cdef int extendAmount = max(0, length - len(myList))
    cdef list extension = [element] * extendAmount
    if direction == "LEFT":
        return extension + myList
    elif direction == "RIGHT":
        return myList + extension
    else:
        raise ValueError("direction has to be in {'LEFT', 'RIGHT'}")

def fill_CList(CList myList, str direction, int length, element):
    cdef int extendAmount = max(0, length - len(myList))
    cdef CList extension = type(myList).fromValues([element]).repeated(length = extendAmount)
    if direction == "LEFT":
        return extension + myList
    elif direction == "RIGHT":
        return myList + extension
    else:
        raise ValueError("direction has to be in {'LEFT', 'RIGHT'}")
