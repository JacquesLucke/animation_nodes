import bpy
from bpy.props import *
from ... utils.nodes import idToSocket
from ... base_types.template import Template

class NewGeneratorOutput(bpy.types.Operator, Template):
    bl_idname = "an.new_loop_generator_output"
    bl_label = "New Loop Generator Output"

    loopIdentifier = StringProperty()
    dataType = StringProperty(default = "Vector List")

    def insert(self):
        node = self.newNode("an_LoopGeneratorOutputNode")
        node.loopInputIdentifier = self.loopIdentifier
        node.listDataType = self.dataType

class NewAssignParameterNode(bpy.types.Operator, Template):
    bl_idname = "an.new_loop_assign_parameter_node"
    bl_label = "New Loop Assign Parameter Node"

    socketID = StringProperty()

    def insert(self):
        socket = idToSocket(eval(self.socketID))
        node = self.newNode("an_ReassignLoopParameterNode")
        node.loopInputIdentifier = socket.node.identifier
        node.parameterIdentifier = socket.identifier
