import bpy
from bpy.props import *
from mathutils import Euler
from ... base_types import AnimationNode
from ... events import propertyChanged
from ... utils.math import composeMatrix

frameTypeItems = [
    ("OFFSET", "Offset", "", 0),
    ("ABSOLUTE", "Absolute", "", 1) ]

class EvaluateFCurvesTransformsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateFCurvesTransformsNode"
    bl_label = "Evaluate FCurves Transforms"

    frameType: EnumProperty(
        name = "Frame Type", default = "OFFSET",
        items = frameTypeItems, update = propertyChanged)

    def create(self):
        self.newInput("FCurve List", "FCurves", "fCurves")
        self.newInput("Float", "Frame", "frame")
        self.newOutput("Matrix", "Matrix", "matrix")
        self.newOutput("Float", "Frame", "outFrame")

    def draw(self, layout):
        layout.prop(self, "frameType", text = "Frame")

    def execute(self, fCurves, frame):
        evaluationFrame = frame
        if self.frameType == "OFFSET":
            evaluationFrame += self.nodeTree.scene.frame_current_final
        transforms = {"location": [0, 0, 0], "rotation_euler": [0, 0, 0], "scale": [1, 1, 1]}
        maxFrame = 0
        for fcurve in fCurves:
            if fcurve.data_path in transforms:
                transforms[fcurve.data_path][fcurve.array_index] = fcurve.evaluate(evaluationFrame)
                maxFrame = max(maxFrame, fcurve.range()[1])
        matrix = composeMatrix(
            transforms["location"],
            Euler(tuple(transforms["rotation_euler"])),
            transforms["scale"],
        )
        return matrix, frame - maxFrame
