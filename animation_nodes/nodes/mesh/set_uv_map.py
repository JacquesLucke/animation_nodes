import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures import VirtualVector2DList

mapIdentifierTypeItems = [
    ("INDEX", "Index", "Get uv map based on the index", "NONE", 0),
    ("NAME", "Name", "Get uv map based on the name", "NONE", 1)
]

class SetUVMapNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetUVMapNode"
    bl_label = "Set UV Map"
    errorHandlingType = "EXCEPTION"

    mapIdentifierType: EnumProperty(name = "UV Map Identifier Type", default = "INDEX",
        items = mapIdentifierTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        if self.mapIdentifierType == "INDEX":
            self.newInput("Integer", "UV Map Index", "uvMapIndex")
        elif self.mapIdentifierType == "NAME":
            self.newInput("Text", "Name", "uvMapName")

        self.newInput("Vector 2D List", "Vectors", "vectors")

        self.newOutput("Object", "Object", "object")

    def drawAdvanced(self, layout):
        layout.prop(self, "mapIdentifierType", text = "Type")

    def execute(self, object, identifier, vectors):
        if object is None:
            return object

        uvMap = self.getUVMap(object, identifier)
        VirtualVector2DList.create(vectors, [0, 0]).materialize(len(uvMap.data))

        uvMap.data.foreach_set('uv', vectors.asNumpyArray())
        object.update_tag()
        return object

    def getUVMap(self, object, identifier):
        if object.type != "MESH":
            self.raiseErrorMessage("Object is not a mesh object.")

        try: return object.data.uv_layers[identifier]
        except: self.raiseErrorMessage("UV map is not found.")
