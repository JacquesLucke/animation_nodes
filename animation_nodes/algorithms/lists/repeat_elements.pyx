import functools
from ... data_structures cimport CList, PolygonIndicesList, LongList
from ... sockets.info import getSocketClass, isCopyable, toBaseDataType, getCopyFunction

def repeatElements(str dataType, myList, LongList amounts, bint makeElementCopies):
    function = getRepeatElementsFunction(dataType, makeElementCopies)
    return function(myList, amounts)

def getRepeatElementsFunction(str dataType, bint makeElementCopies = True):
    socketClass = getSocketClass(dataType)
    defaultValue = socketClass.getDefaultValue()

    if isinstance(defaultValue, list):
        baseDataType = toBaseDataType(dataType)
        if isCopyable(baseDataType) and makeElementCopies:
            return functools.partial(repeat_PythonList_Copy, getCopyFunction(baseDataType))
        else:
            return repeat_PythonList_NoCopy
    elif isinstance(defaultValue, CList):
        return repeat_CList
    elif isinstance(defaultValue, PolygonIndicesList):
        return repeat_PolygonIndicesList
    else:
        raise NotImplementedError()

def repeat_PythonList_NoCopy(list myList, LongList amounts):
    return [e for i, e in enumerate(myList) for _ in range(amounts.data[i])]

def repeat_PythonList_Copy(copyFunction, list myList, LongList amounts):
    return [copyFunction(e) for i, e in enumerate(myList) for _ in range(amounts.data[i])]

def repeat_CList(CList myList, LongList amounts):
    return myList.repeatedPerElement(amounts)

def repeat_PolygonIndicesList(PolygonIndicesList myList, LongList amounts):
    return myList.repeatedPerElement(amounts)

