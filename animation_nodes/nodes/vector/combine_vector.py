import bpy
from bpy.props import *
from ... data_structures import Vector3DList, DoubleList
from ... base_types import AnimationNode, AutoSelectVectorization
from . list_operation_utils import combineDoubleListsToVectorList

class CombineVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineVectorNode"
    bl_label = "Combine Vector"
    dynamicLabelType = "HIDDEN_ONLY"

    useListX = BoolProperty(update = AnimationNode.updateSockets)
    useListY = BoolProperty(update = AnimationNode.updateSockets)
    useListZ = BoolProperty(update = AnimationNode.updateSockets)

    errorMessage = StringProperty()

    def create(self):
        self.newInputGroup(self.useListX,
            ("Float", "X", "x"),
            ("Float List", "X", "x"))

        self.newInputGroup(self.useListY,
            ("Float", "Y", "y"),
            ("Float List", "Y", "y"))

        self.newInputGroup(self.useListZ,
            ("Float", "Z", "z"),
            ("Float List", "Z", "z"))

        self.newOutputGroup(self.generatesList,
            ("Vector", "Vector", "vector"),
            ("Vector List", "Vectors", "vectors"))

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useListX", self.inputs[0])
        vectorization.input(self, "useListY", self.inputs[1])
        vectorization.input(self, "useListZ", self.inputs[2])
        vectorization.output(self, self.outputs[0], dependencies = [("useListX", "useListY", "useListZ")])
        self.newSocketEffect(vectorization)

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawLabel(self):
        label = "<X, Y, Z>"
        for axis in "XYZ":
            if not getattr(self, "useList" + axis):
                label = label.replace(axis, str(round(self.inputs[axis].value, 4)))
        return label

    def getExecutionCode(self):
        if self.generatesList:
            yield "vectors = self.createVectorList(x, y, z)"
        else:
            yield "vector = Vector((x, y, z))"

    def createVectorList(self, x, y, z):
        self.errorMessage = ""
        _x, _y, _z = self.prepareInputLists(x, y, z)
        if _x is None: return Vector3DList()
        return combineDoubleListsToVectorList(_x, _y, _z)

    def prepareInputLists(self, x, y, z):
        maxLength = max(len(l) for l in (x, y, z) if isinstance(l, DoubleList))
        if any(len(l) != maxLength for l in (x, y, z) if isinstance(l, DoubleList)):
            self.errorMessage = "lists have different length"
            return None, None, None

        if isinstance(x, DoubleList): _x = x
        else: _x = DoubleList.fromValues((x, )) * maxLength
        if isinstance(y, DoubleList): _y = y
        else: _y = DoubleList.fromValues((y, )) * maxLength
        if isinstance(z, DoubleList): _z = z
        else: _z = DoubleList.fromValues((z, )) * maxLength
        return _x, _y, _z

    @property
    def generatesList(self):
        return any((self.useListX, self.useListY, self.useListZ))
