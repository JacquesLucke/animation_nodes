import bpy
import numpy as np
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures import DoubleList, VirtualDoubleList

mapIdentifierTypeItems = [
    ("INDEX", "Index", "Get uv map based on the index", "NONE", 0),
    ("NAME", "Name", "Get uv map based on the name", "NONE", 1)
]

class UVMapDataInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_UVMapDataInputNode"
    bl_label = "UV Map Data Input"
    errorHandlingType = "EXCEPTION"

    mapIdentifierType: EnumProperty(name = "UV Map Identifier Type", default = "INDEX",
        items = mapIdentifierTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        if self.mapIdentifierType == "INDEX":
            self.newInput("Integer", "UV Map Index", "uvMapIndex")
        elif self.mapIdentifierType == "NAME":
            self.newInput("Text", "Name", "uvMapName")

        self.newOutput("Float List", "X", "x")
        self.newOutput("Float List", "Y", "y")

    def drawAdvanced(self, layout):
        layout.prop(self, "mapIdentifierType", text = "Type")

    def execute(self, object, identifier):
        if object is None:
            return DoubleList(), DoubleList()

        uvMap = self.getUVMap(object, identifier)

        x = VirtualDoubleList.create(0, 0)
        y = VirtualDoubleList.create(0, 0)

        coList = np.zeros((2 * len(uvMap.data)), dtype=float)
        uvMap.data.foreach_get('uv', coList)
        x = coList[::2]
        y = coList[1::2]
        return DoubleList.fromValues(x), DoubleList.fromValues(y)

    def getUVMap(self, object, identifier):
        if object.type != "MESH":
            self.raiseErrorMessage("Object is not a mesh object.")

        try: return object.data.uv_layers[identifier]
        except: self.raiseErrorMessage("UV Map is not found.")
