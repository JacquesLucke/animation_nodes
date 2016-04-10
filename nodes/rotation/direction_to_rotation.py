import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

trackAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]
guideAxisItems  = [(axis, axis, "") for axis in ("X", "Y", "Z")]

class DirectionToRotationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DirectionToRotationNode"
    bl_label = "Direction to Rotation"

    trackAxis = EnumProperty(items = trackAxisItems, update = propertyChanged, default = "Z")
    guideAxis = EnumProperty(items = guideAxisItems, update = propertyChanged, default = "X")

    def create(self):
        self.newInput("an_VectorSocket", "Direction", "direction")
        self.newInput("an_VectorSocket", "Guide", "guide").value = [0.0, 0.0, 1.0]
        self.newOutput("an_EulerSocket", "Euler Rotation", "eulerRotation")
        self.newOutput("an_QuaternionSocket", "Quaternion Rotation", "quaternionRotation").hide = True
        self.newOutput("an_MatrixSocket", "Matrix Rotation", "matrixRotation").hide = True
        self.width += 20

    def draw(self, layout):
        layout.prop(self, "trackAxis", expand = True)
        layout.prop(self, "guideAxis", expand = True)

        if self.trackAxis[-1:] == self.guideAxis[-1:]:
            layout.label("Must be different", icon = "ERROR")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()

        yield "matrixRotation = animation_nodes.algorithms.rotation.generateRotationMatrix(direction, guide, self.trackAxis, self.guideAxis)"
        if isLinked["matrixRotation"]: yield "matrixRotation.normalize()"
        if isLinked["eulerRotation"]: yield "eulerRotation = matrixRotation.to_euler()"
        if isLinked["quaternionRotation"]: yield "quaternionRotation = matrixRotation.to_quaternion()"
