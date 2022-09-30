import bpy
from bpy.props import *
from ... base_types import AnimationNode, DataTypeSelectorSocket

compareTypeItems = [
    ("A=B", "A = B", "", "NONE", 0),
    ("A!=B", "A != B", "", "NONE", 1),
    ("A<B", "A < B", "", "NONE", 2),
    ("A<=B", "A <= B", "", "NONE", 3),
    ("A>B", "A > B", "", "NONE", 4),
    ("A>=B", "A >= B", "", "NONE", 5),
    ("A_IS_B", "A is B", "", "NONE", 6),
    ("A_IS_NONE", "A is None", "", "NONE", 7),
]

numericLabelTypes = ["Integer", "Float"]

class CompareNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_CompareNode"
    bl_label = "Compare"
    dynamicLabelType = "HIDDEN_ONLY"

    assignedType: DataTypeSelectorSocket.newProperty(default = "Integer")

    compareType: EnumProperty(name = "Compare Type",
        items = compareTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput(DataTypeSelectorSocket("A", "a", "assignedType"))
        if self.compareType != "A_IS_NONE":
            self.newInput(DataTypeSelectorSocket("B", "b", "assignedType"))

        self.newOutput("Boolean", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "compareType", text = "Type")

    def drawLabel(self):
        label = [item[1] for item in compareTypeItems if self.compareType == item[0]][0]
        if self.assignedType in numericLabelTypes and len(self.inputs) == 2:
            if getattr(self.socketA, "isUnlinked", False):
                label = label.replace("A", str(round(self.socketA.value, 4)))
            if getattr(self.socketB, "isUnlinked", False):
                label = label.replace("B", str(round(self.socketB.value, 4)))
        return label

    def drawAdvanced(self, layout):
        self.invokeSelector(layout, "DATA_TYPE", "assignType",
            text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self, required):
        type = self.compareType
        if type == "A=B":     return "result = a == b"
        if type == "A!=B":    return "result = a != b"
        if type == "A<B":	    return "try: result = a < b \nexcept: result = False"
        if type == "A<=B":    return "try: result = a <= b \nexcept: result = False"
        if type == "A>B":	    return "try: result = a > b \nexcept: result = False"
        if type == "A>=B":    return "try: result = a >= b \nexcept: result = False"
        if type == "A_IS_B":    return "result = a is b"
        if type == "A_IS_NONE": return "result = a is None"
        return "result = False"

    def assignType(self, dataType):
        if self.assignedType != dataType:
            self.assignedType = dataType
            self.refresh()

    @property
    def socketA(self):
        return self.inputs.get("A")

    @property
    def socketB(self):
        return self.inputs.get("B")
