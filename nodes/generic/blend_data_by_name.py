import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

dataTypes = {
    "Object" : "objects",
    "Scene" : "scenes",
    "Object Group" : "groups",
    "Text Block" : "texts" }

class BlendDataByNameNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BlendDataByNameNode"
    bl_label = "Data by Name"
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [(name + " by Name", {"dataType" : repr(name)}) for name in dataTypes.keys()]

    def dataTypeChanged(self, context):
        self.createSockets()

    # Should be set only on node creation
    dataType = StringProperty(name = "Data Type", update = dataTypeChanged)

    def create(self):
        self.dataType = "Object"

    def drawLabel(self):
        return self.dataType + " by Name"

    def getExecutionCode(self):
        return "output = bpy.data.{}.get(name)".format(dataTypes[self.dataType])

    @keepNodeState
    def createSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.newInput("String", "Name", "name").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput(self.dataType, self.dataType, "output")
