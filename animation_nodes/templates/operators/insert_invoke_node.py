import bpy
from bpy.props import *
from ... base_types import Template
from ... tree_info import getNodeByIdentifier

class InsertInvokeNode(bpy.types.Operator, Template):
    bl_idname = "an.insert_invoke_node_template_operator"
    bl_label = "Insert Invoke Node"

    subprogramIdentifier = StringProperty()

    def insert(self):
        invokeNode = self.newNode("an_InvokeSubprogramNode")
        invokeNode.subprogramIdentifier = self.subprogramIdentifier
