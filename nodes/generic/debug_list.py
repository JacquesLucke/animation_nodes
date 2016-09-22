import bpy
from bpy.props import *
from ... base_types import AnimationNode, UpdateAssignedDataType

class DebugListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DebugListNode"
    bl_label = "Debug List"

    textBlockName = StringProperty(name = "Text")
    dataType = StringProperty(default = "Generic", update = AnimationNode.updateSockets)
    inputIsIterable = BoolProperty(default = False)

    def create(self):
        self.newInput("Text Block", "Text", "text")
        self.newInput(self.dataType, "Data", "data")
        self.newSocketEffect(UpdateAssignedDataType(
            "dataType", [self.inputs[1]], default = "Generic"))

    def draw(self, layout):
        if not self.inputIsIterable:
            layout.label("No List Type", icon = "ERROR")

    def execute(self, text, data):
        self.inputIsIterable = True
        if text is None: return

        text.clear()
        if self.dataType in ("Float List", "Color"):
            text.write("\n".join([str(round(e, 4)) for e in data]))
        else:
            try: text.write("\n".join([str(e) for e in data]))
            except: self.inputIsIterable = False
