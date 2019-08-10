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

class UVMapDataOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_UVMapDataOutputNode"
    bl_label = "UV Map Data Output"

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
        if object is None or object.type != "MESH" or object.mode != "OBJECT":
            return object
        uvMap = self.getUVMap(object, identifier)
        if uvMap is None:
            return object
        if len(x) == 0 or len(y) == 0:
            return object
        end = len(x) + len(y) 
        coList = np.zeros((end), dtype=float)
        coList[:end:2] = np.array(x)
        coList[1:end:2] = np.array(y)
        uvMap.data.foreach_set('uv', coList)
        object.update_tag()
        return object

    def getUVMap(self, object, identifier):
        try: return object.data.uv_layers[identifier]
        except: return object.data.uv_layers.new(name="UVMap", do_init=True)