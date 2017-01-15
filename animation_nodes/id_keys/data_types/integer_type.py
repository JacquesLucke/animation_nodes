from . base import SingleIDKeyDataType
from ... data_structures import LongLongList
from ... utils.operators import makeOperator
from ... utils.selection import getSortedSelectedObjects

class IntegerDataType(SingleIDKeyDataType):
    identifier = "Integer"
    default = 0

    @classmethod
    def getList(cls, objects, name):
        default = cls.default
        path = cls.getPath(name)
        return LongLongList.fromValues(getattr(object, path, default) for object in objects)

    @classmethod
    def drawExtras(cls, layout, object, name):
        props = layout.operator("an.id_keys_from_selection_order")
        props.name = name

@makeOperator("an.id_keys_from_selection_order", "From Selection Order", arguments = ["String"])
def idKeyFromSelectionOrder(name):
    for i, object in enumerate(getSortedSelectedObjects()):
        object.id_keys.set("Integer", name, i)
