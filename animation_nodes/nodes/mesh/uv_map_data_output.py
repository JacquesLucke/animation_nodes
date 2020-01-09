import bpy
import numpy as np
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures import VirtualDoubleList

mapIdentifierTypeItems = [
    ("INDEX", "Index", "Get uv map based on the index", "NONE", 0),
    ("NAME", "Name", "Get uv map based on the name", "NONE", 1)
]

class UVMapDataOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_UVMapDataOutputNode"
    bl_label = "UV Map Data Output"
    errorHandlingType = "EXCEPTION"

    mapIdentifierType: EnumProperty(name = "UV Map Identifier Type", default = "INDEX",
        items = mapIdentifierTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        if self.mapIdentifierType == "INDEX":
            self.newInput("Integer", "UV Map Index", "uvMapIndex")
        elif self.mapIdentifierType == "NAME":
            self.newInput("Text", "Name", "uvMapName")

        self.newInput("Float List", "X", "x")
        self.newInput("Float List", "Y", "y")

        self.newOutput("Object", "Object", "object")

    def drawAdvanced(self, layout):
        layout.prop(self, "mapIdentifierType", text = "Type")

    def execute(self, object, identifier, x, y):
        if object is None:
            return object

        uvMap = self.getUVMap(object, identifier)

        coLength = len(uvMap.data)
        xList = VirtualDoubleList.create(x, 0).materialize(coLength)
        yList = VirtualDoubleList.create(y, 0).materialize(coLength)

        coList = np.zeros(2 * coLength, dtype = float)
        coList[::2] = xList.asNumpyArray()
        coList[1::2] = yList.asNumpyArray()

        uvMap.data.foreach_set('uv', coList)
        object.update_tag()
        return object

    def getUVMap(self, object, identifier):
        if object.type != "MESH":
            self.raiseErrorMessage("Object is not a mesh object.")

        try: return object.data.uv_layers[identifier]
        except: return object.data.uv_layers.new(name = "UVMap", do_init = True)
