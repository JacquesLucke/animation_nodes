import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... utils.hash import hashStringToNumber

dataTypes = {
    "Object" : ("an_ObjectSocket", "objects"),
    "Scene" : ("an_SceneSocket", "scenes"),
    "Object Group" : ("an_ObjectGroupSocket", "groups"),
    "Text Block" : ("an_TextBlockSocket", "texts") }

class BlendDataByNameNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BlendDataByNameNode"
    bl_label = "Data by Name"

    onlySearchTags = True
    searchTags = [(name + " by Name", {"dataType" : repr(name)}) for name in dataTypes.keys()]

    def dataTypeChanged(self, context):
        self.createSockets()
        executionCodeChanged()

    # Should be set only on node creation
    dataType = StringProperty(name = "Data Type", update = dataTypeChanged)

    def create(self):
        self.dataType = "Object"

    def getExecutionCode(self):
        space = "bpy.data." + dataTypes[self.dataType][1]
        yield "output = {0}.get(name)".format(space)

    def createSockets(self):
        idName = dataTypes[self.dataType]
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new("an_StringSocket", "Name", "name").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new(dataTypes[self.dataType][0], self.dataType, "output")
