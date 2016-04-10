import bpy
from ... base_types.node import AnimationNode

class VectorAngleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorAngleNode"
    bl_label = "Vector Angle"

    def create(self):
        self.newInput("an_VectorSocket", "A", "a").value = [1, 0, 0]
        self.newInput("an_VectorSocket", "B", "b").value = [0, 0, 1]
        self.newOutput("an_FloatSocket", "Angle", "angle")
        self.newOutput("an_QuaternionSocket", "Rotation Difference", "rotationDifference")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        
        if isLinked["angle"]: yield "angle = a.angle(b, 0.0)"
        if isLinked["rotationDifference"]: yield "rotationDifference = a.rotation_difference(b)"
