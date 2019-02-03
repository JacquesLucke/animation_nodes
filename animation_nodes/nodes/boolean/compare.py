import bpy
from bpy.props import *
from ... base_types import AnimationNode, DataTypeSelectorSocket

compare_types = ["A = B", "A != B", "A < B", "A <= B", "A > B", "A >= B", "A is B","A is None"]
compare_types_items = [(t, t, "") for t in compare_types]

numericTypes = ("Integer", "Float")

class CompareNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CompareNode"
    bl_label = "Compare"
    dynamicLabelType = "HIDDEN_ONLY"

    assignedType: DataTypeSelectorSocket.newProperty(default = "Integer")

    compareType: EnumProperty(name = "Compare Type",
        items = compare_types_items, update = AnimationNode.refresh)

    elementwise: BoolProperty(name = "Elementwise", default = False, update = AnimationNode.refresh)

    def create(self):
        self.newInput(DataTypeSelectorSocket("A", "a", "assignedType"))
        if self.compareType != "A is None":
            self.newInput(DataTypeSelectorSocket("B", "b", "assignedType"))

        if "List" in self.assignedType and self.elementwise:
            self.newOutput("Boolean List", "Result", "result")
        else:
            self.newOutput("Boolean", "Result", "result")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "compareType", text = "")
        row.prop(self, "elementwise", text = "", icon = "LINENUMBERS_ON")

    def drawLabel(self):
        label = self.compareType
        if self.assignedType in numericTypes and len(self.inputs) == 2:
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
        if "List" in self.assignedType and self.elementwise:
            if self.assignedType == "Integer List":
                if type == "A = B": return "result = AN.nodes.boolean.compare_c_utils.equal_LongList(a, b)"
                if type == "A != B": return "result = AN.nodes.boolean.compare_c_utils.notEqual_LongList(a, b)"
                if type == "A > B": return "result = AN.nodes.boolean.compare_c_utils.greater_LongList(a, b)"
                if type == "A >= B": return "result = AN.nodes.boolean.compare_c_utils.greaterEqual_LongList(a, b)"
                if type == "A < B": return "result = AN.nodes.boolean.compare_c_utils.less_LongList(a, b)"
                if type == "A <= B": return "result = AN.nodes.boolean.compare_c_utils.lessEqual_LongList(a, b)"
            elif self.assignedType == "Float List":
                if type == "A = B": return "result = AN.nodes.boolean.compare_c_utils.equal_DoubleList(a, b)"
                if type == "A != B": return "result = AN.nodes.boolean.compare_c_utils.notEqual_DoubleList(a, b)"
                if type == "A > B": return "result = AN.nodes.boolean.compare_c_utils.greater_DoubleList(a, b)"
                if type == "A >= B": return "result = AN.nodes.boolean.compare_c_utils.greaterEqual_DoubleList(a, b)"
                if type == "A < B": return "result = AN.nodes.boolean.compare_c_utils.less_DoubleList(a, b)"
                if type == "A <= B": return "result = AN.nodes.boolean.compare_c_utils.lessEqual_DoubleList(a, b)"
            else:
                if type == "A = B": return "result = [x == y for x, y in zip(a, b)]"
                if type == "A != B": return "result = [x != y for x, y in zip(a, b)]"
                if type == "A is B": return "result = [x is y for x, y in zip(a, b)]"
                if type == "A is None": return "result = [x is None for x in a]"
            return "result = BooleanList.fromValue(False, length = len(a))"
        else:
            if type == "A = B":     return "result = a == b"
            if type == "A != B":    return "result = a != b"
            if type == "A is B":    return "result = a is b"
            if type == "A is None": return "result = a is None"
            if self.assignedType in numericTypes:
                if type == "A < B":	    return "result = a < b"
                if type == "A <= B":    return "result = a <= b"
                if type == "A > B":	    return "result = a > b"
                if type == "A >= B":    return "result = a >= b"
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
