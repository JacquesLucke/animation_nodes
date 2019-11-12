import bpy
import numpy as np
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import DoubleList
from ... base_types import AnimationNode

mapIdentifierTypeItems = [
    ("INDEX", "Index", "Get uv map based on the index", "NONE", 0),
    ("NAME", "Name", "Get uv map based on the name", "NONE", 1)
]

class UVMapDataInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_UVMapDataInputNode"
    bl_label = "UV Map Data Input"

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
        x = []
        y = []
        if object is None:
            return DoubleList.fromValues(x), DoubleList.fromValues(y)
        uvMap = self.getUVMap(object, identifier)
        if uvMap is None:
            return DoubleList.fromValues(x), DoubleList.fromValues(y)
        coList = np.zeros((2 * len(uvMap.data)), dtype=float)
        uvMap.data.foreach_get('uv', coList)
        x = coList[::2]
        y = coList[1::2]
        return DoubleList.fromValues(x), DoubleList.fromValues(y)

    def getUVMap(self, object, identifier):
        try: return object.data.uv_layers[identifier]
        except: return None