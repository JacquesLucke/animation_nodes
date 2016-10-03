from . base import SingleIDKeyDataType
from ... data_structures import LongLongList

class IntegerDataType(SingleIDKeyDataType):
    identifier = "Integer"
    default = 0

    @classmethod
    def getList(cls, objects, name):
        default = cls.default
        path = cls.getPath(name)
        return LongLongList.fromValues(getattr(object, path, default) for object in objects)
