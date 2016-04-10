import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class DebugListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DebugListNode"
    bl_label = "Debug List"

    textBlockName = StringProperty(name = "Text")
    dataType = StringProperty()
    inputIsIterable = BoolProperty(default = False)

    def create(self):
        self.newInput("Text Block", "Text", "text")
        self.newInput("Generic", "Data", "data")

    def draw(self, layout):
        if not self.inputIsIterable:
            layout.label("No List Type", icon = "ERROR")

    def edit(self):
        inputSocket = self.inputs[1]
        dataOrigin = inputSocket.dataOrigin
        if dataOrigin is None: self.dataType = ""
        else: self.dataType = dataOrigin.dataType

    def execute(self, text, data):
        self.inputIsIterable = True
        if text is None: return

        text.clear()
        if self.dataType in ("Float List", "Color"):
            text.write("\n".join([str(round(e, 4)) for e in data]))
        else:
            try: text.write("\n".join([str(e) for e in data]))
            except: self.inputIsIterable = False
