import bpy
from bpy.props import *
from ... base_types import Template
from ... sockets.info import isList, toBaseDataType

class InsertDataInputNodeTemplateOperator(bpy.types.Operator, Template):
    bl_idname = "an.insert_data_input_node_template_operator"
    bl_label = "Insert Data Input Node"

    socketIndex = IntProperty(default = 0)

    @property
    def needsMenu(self):
        return len(self.activeNode.getVisibleInputs()) > 1

    def drawMenu(self, layout):
        layout.operator_context = "EXEC_DEFAULT"
        for socket in self.activeNode.getVisibleInputs():
            props = layout.operator(self.bl_idname, text = socket.getDisplayedName())
            props.socketIndex = socket.getIndex()

    def insert(self):
        activeNode = self.activeNode
        if self.usedMenu: socket = activeNode.inputs[self.socketIndex]
        else: socket = activeNode.getVisibleInputs()[0]

        if isList(socket.bl_idname):
            originNode = self.newNode("an_CreateListNode")
            originNode.assignedType = toBaseDataType(socket.bl_idname)
        else:
            originNode = self.newNode("an_DataInputNode")
            originNode.assignedType = socket.dataType
            originNode.inputs[0].setProperty(socket.getProperty())

        socket.linkWith(originNode.outputs[0])
        self.setActiveNode(originNode)
