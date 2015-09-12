import bpy
from bpy.props import *
from ... base_types.template import Template

subprogramTypeItems = [
    ("GROUP", "Group", ""),
    ("LOOP", "Loop", ""),
    ("SCRIPT", "Script", "") ]

class EmptySubprogramTemplate(bpy.types.Operator, Template):
    bl_idname = "an.empty_subprogram_template"
    bl_label = "Empty Subprogram"

    subprogramType = EnumProperty(name = "Subprogram Type", items = subprogramTypeItems)

    # optional
    targetNodeIdentifier = StringProperty(default = "")

    def drawMenu(self, layout):
        layout.prop(self, "subprogramType")

    def insert(self):
        if self.subprogramType == "GROUP":
            identifier = self.insertGroup()
        if self.subprogramType == "LOOP":
            identifier = self.insertLoop()
        if self.subprogramType == "SCRIPT":
            identifier = self.insertScript()

        targetNode = self.nodeByIdentifier(self.targetNodeIdentifier)
        if targetNode:
            targetNode.subprogramIdentifier = identifier

    def insertGroup(self):
        inputNode = self.newNode("an_GroupInputNode")
        outputNode = self.newNode("an_GroupOutputNode", x = 500)
        outputNode.groupInputIdentifier = inputNode.identifier
        return inputNode.identifier

    def insertLoop(self):
        return self.newNode("an_LoopInputNode").identifier

    def insertScript(self):
        return self.newNode("an_ScriptNode").identifier
