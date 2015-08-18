import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged
from ... sockets.info import toIdName
from ... tree_info import keepNodeLinks

compare_types = ["A = B", "A != B", "A < B", "A <= B", "A > B", "A >= B", "A is B"]
compare_types_items = [(t, t, "") for t in compare_types]

class CompareNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CompareNode"
    bl_label = "Compare"

    inputNames = { "A" : "a",
                   "B" : "b" }
    outputNames = { "Result" : "result" }

    def assignedTypeChanged(self, context):
        self.inputIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    inputIdName = StringProperty()
    compareType = EnumProperty(name = "Compare Type", items = compare_types_items, update = executionCodeChanged)

    def create(self):
        self.assignedType = "Float"
        self.outputs.new("an_BooleanSocket", "Result")

    def draw(self, layout):
        layout.prop(self, "compareType", text = "Type")

    def getExecutionCode(self):
        type = self.compareType
        if type == "A = B":	return "$result$ = %a% == %b%"
        if type == "A != B": return "$result$ = %a% != %b%"
        if type == "A < B":	return "try: $result$ = %a% < %b% \nexcept: $result$ = False"
        if type == "A <= B": return "try: $result$ = %a% <= %b% \nexcept: $result$ = False"
        if type == "A > B":	return "try: $result$ = %a% > %b% \nexcept: $result$ = False"
        if type == "A >= B": return "try: $result$ = %a% >= %b% \nexcept: $result$ = False"
        if type == "A is B": return "$result$ = %a% is %b%"
        return "$result$ = False"

    def edit(self):
        dataType = self.getWantedDataType()
        self.assingType(dataType)

    def getWantedDataType(self):
        inputA = self.inputs[0].dataOriginSocket
        inputB = self.inputs[1].dataOriginSocket

        if inputA is not None: return inputA.dataType
        if inputB is not None: return inputB.dataType
        return self.inputs[0].dataType

    def assingType(self, dataType):
        if self.assignedType == dataType: return
        self.assignedType = dataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        self.inputs.new(self.inputIdName, "A")
        self.inputs.new(self.inputIdName, "B")
