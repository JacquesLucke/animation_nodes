import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, AutoSelectVectorization

directionAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]

class RotationToDirectionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RotationToDirectionNode"
    bl_label = "Rotation to Direction"
    bl_width_default = 160

    useRotationList = BoolProperty(update = AnimationNode.refresh)

    directionAxis = EnumProperty(items = directionAxisItems, update = propertyChanged, default = "Z")

    def create(self):
        self.newInputGroup(self.useRotationList,
            ("Euler", "Rotation", "rotation"),
            ("Euler List", "Rotations", "rotations"))

        self.newInput("Float", "Length", "length", value = 1)

        self.newOutputGroup(self.useRotationList,
            ("Vector", "Direction", "direction"),
            ("Vector List", "Directions", "directions"))

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useRotationList", self.inputs[0])
        vectorization.output(self, "useRotationList", self.outputs[0])
        self.newSocketEffect(vectorization)

    def draw(self, layout):
        layout.prop(self, "directionAxis", expand = True)

    def getExecutionCode(self):
        if self.useRotationList:
            yield "directions = AN.algorithms.rotations.eulersToDirections(rotations, self.directionAxis)"
            yield "AN.math.scaleVector3DList(directions, length)"
        else:
            yield "direction = AN.algorithms.rotations.eulerToDirection(rotation, self.directionAxis)"
            yield "direction *= length"
