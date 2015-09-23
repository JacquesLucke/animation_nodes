import bpy
from bpy.props import *
from ... base_types.template import Template

class InsertDebugNodeTemplateOperator(bpy.types.Operator, Template):
    bl_idname = "an.insert_debug_node_template_operator"
    bl_label = "Insert Debug Node"

    socketIndex = IntProperty(default = 0)

    @property
    def needsMenu(self):
        return len(self.activeNode.getVisibleOutputs()) > 1

    def drawMenu(self, layout):
        layout.operator_context = "EXEC_DEFAULT"
        for socket in self.activeNode.getVisibleOutputs():
            props = layout.operator(self.bl_idname, text = socket.getDisplayedName())
            props.socketIndex = socket.index

    def insert(self):
        activeNode = self.activeNode
        debugNode = self.newNode("an_DebugNode")

        if self.usedMenu: socket = activeNode.outputs[self.socketIndex]
        else: socket = activeNode.getVisibleOutputs()[0]
        socket.linkWith(debugNode.inputs[0])

        self.setActiveNode(debugNode)
