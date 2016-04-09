import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

compareTypeItems = [
    ("ANY", "Any", ""), 
    ("ALL", "All", ""),
    ("NOT_ANY", "not Any", ""), 
    ("NOT_ALL", "not All", "")]
compareFormula = { t[0] : t[1].lower() for t in compareTypeItems }
compareLabels = { t[0] : t[1] for t in compareTypeItems }

class CompareBoolListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CompareBoolListNode"
    bl_label = "Compare Bool List"
    dynamicLabelType = "HIDDEN_ONLY"
    searchTags = ["Compare Boolean List", "Logic Boolean List"]

    compareType = EnumProperty(name = "Compare Type", default = "ANY",
        items = compareTypeItems, update = executionCodeChanged)

    def create(self):
        self.assignedType = "Float"
        self.inputs.new("an_BooleanListSocket", "Boolean List", "list")
        self.outputs.new("an_BooleanSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "compareType", text = "")

    def drawLabel(self):
        return compareLabels[self.compareType]

    def getExecutionCode(self):
        return ("try: result = {}(list)\nexcept: result = False"
                        .format(compareFormula[self.compareType]) )