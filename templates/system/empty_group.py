import bpy
from ... base_types.template import Template

class EmptyGroupTemplate(bpy.types.Operator, Template):
    bl_idname = "an.empty_group_template"
    bl_label = "Empty Group"

    def insert(self):
        inputNode = self.newNode("an_GroupInputNode")
        outputNode = self.newNode("an_GroupOutputNode", x = 500)
        outputNode.groupInputIdentifier = inputNode.identifier
