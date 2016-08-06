import bpy
from .. data_structures import EdgeIndicesList
from .. base_types.socket import AnimationNodeSocket, ListSocket

class EdgeIndicesSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EdgeIndicesSocket"
    bl_label = "Edge Indices Socket"
    dataType = "Edge Indices"
    allowedInputTypes = ["Edge Indices"]
    drawColor = (0.4, 0.6, 0.6, 1)
    comparable = True
    storable = True

    @classmethod
    def getDefaultValue(cls):
        return (0, 1)

    @classmethod
    def getDefaultValueCode(cls):
        return "(0, 1)"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"

    @classmethod
    def correctValue(cls, value):
        if isEdge(value): return value, 0
        else: return cls.getDefaultValue(), 2


class EdgeIndicesListSocket(bpy.types.NodeSocket, ListSocket, AnimationNodeSocket):
    bl_idname = "an_EdgeIndicesListSocket"
    bl_label = "Edge Indices List Socket"
    dataType = "Edge Indices List"
    baseDataType = "Edge Indices"
    allowedInputTypes = ["Edge Indices List"]
    drawColor = (0.4, 0.6, 0.6, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return EdgeIndicesList()

    @classmethod
    def getDefaultValueCode(cls):
        return "EdgeIndicesList()"

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def getFromValuesCode(cls):
        return "EdgeIndicesList.fromValues(value)"

    @classmethod
    def getJoinListsCode(cls):
        return "EdgeIndicesList.join(value)"

    @classmethod
    def getReverseCode(cls):
        return "value.reversed()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, EdgeIndicesList):
            return value, 0
        try: return EdgeIndicesList.fromValues(value), 1
        except: return cls.getDefaultValue(), 2
