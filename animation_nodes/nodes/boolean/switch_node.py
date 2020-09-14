import bpy
from bpy.props import *
from ... sockets.info import toListDataType, isList
from ... base_types import AnimationNode, DataTypeSelectorSocket, VectorizedSocket

class SwitchNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SwitchNode"
    bl_label = "Switch"

    assignedType: DataTypeSelectorSocket.newProperty(default = "Float")
    useList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Boolean", "useList",
                    ("Condition", "condition"), ("Conditions", "conditions")))

        self.newInput(DataTypeSelectorSocket("If True", "ifTrue", "assignedType"))
        self.newInput(DataTypeSelectorSocket("If False", "ifFalse", "assignedType"))

        if self.useList:
            if not isList(self.assignedType):
                listDataType = toListDataType(self.assignedType)
                self.newOutput(listDataType, listDataType, "dataList")
            else:
                self.newOutput(self.assignedType, self.assignedType, "dataList")
        else:
            self.newOutput(DataTypeSelectorSocket("Output", "output", "assignedType"))
            self.newOutput(DataTypeSelectorSocket("Other", "other", "assignedType"), hide = True)

    def drawAdvanced(self, layout):
        self.invokeSelector(layout, "DATA_TYPE", "assignType",
            text = "Change Type", icon = "TRIA_RIGHT")

    def assignType(self, dataType):
        if self.assignedType != dataType:
            self.assignedType = dataType
            self.refresh()

    def getExecutionCode(self, required):
        if self.useList:
            if "dataList" in required: yield "dataList = self.execute_list(conditions, ifTrue, ifFalse)"
        else:
            if "output" in required: yield "output = ifTrue if condition else ifFalse"
            if "other" in required:  yield "other = ifFalse if condition else ifTrue"
                
    def execute_list(self, conditions, ifTrue, ifFalse):
        outputs = []
        for condition in conditions:
            if condition:
                outputs.append(ifTrue)
            else:
                outputs.append(ifFalse)
        if not isList(self.assignedType):
            listDataType = toListDataType(self.assignedType)
            return self.outputs[0].correctValue(outputs)[0]
        else:
            outs = []
            for i in range(len(conditions)):
                outs.extend(outputs[i])
            return self.outputs[0].correctValue(outs)[0]
