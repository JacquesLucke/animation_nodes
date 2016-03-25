import bpy
from bpy.props import *
from mathutils import Vector
from ... events import executionCodeChanged
from ... algorithms.rotation import generateDirectionToRotationCode
from ... base_types.node import AnimationNode

trackAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]
guideAxisItems  = [(axis, axis, "") for axis in ("X", "Y", "Z")]

class DirectionToRotationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DirectionToRotationNode"
    bl_label = "Direction to Rotation"

    trackAxis = EnumProperty(items = trackAxisItems, update = executionCodeChanged, default = "Z")
    guideAxis = EnumProperty(items = guideAxisItems, update = executionCodeChanged, default = "X")

    def create(self):
        self.inputs.new("an_VectorSocket", "Direction", "direction")
        self.inputs.new("an_VectorSocket", "Guide", "guide").value = [0.0, 0.0, 1.0]
        self.outputs.new("an_EulerSocket", "Euler Rotation", "eulerRotation")
        self.outputs.new("an_QuaternionSocket", "Quaternion Rotation", "quaternionRotation").hide = True
        self.outputs.new("an_MatrixSocket", "Matrix Rotation", "matrixRotation").hide = True
        self.width += 20

    def draw(self, layout):
        layout.prop(self, "trackAxis", expand = True)
        layout.prop(self, "guideAxis", expand = True)

        if self.trackAxis[-1:] == self.guideAxis[-1:]:
            layout.label("Must be different", icon = "ERROR")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
        
        rot = "eulerRotation" if isLinked["eulerRotation"] else ""
        quat = "quaternionRotation" if isLinked["quaternionRotation"] else ""
        mat = "matrixRotation" if isLinked["matrixRotation"] else ""

        return generateDirectionToRotationCode("direction", "guide", 
                                                self.trackAxis, self.guideAxis, 
                                                matrixOutputName = "{}".format(mat), 
                                                rotationOutputName = "{}".format(rot),
                                                quaternionOutputName = "{}".format(quat))

    def getUsedModules(self):
        return ["mathutils"]
