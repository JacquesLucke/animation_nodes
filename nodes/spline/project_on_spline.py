import bpy
from bpy.props import *
from mathutils import Vector
from ... tree_info import keepNodeState
from ... base_types import AnimationNode

class ProjectOnSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ProjectOnSplineNode"
    bl_label = "Project on Spline"

    def settingChanged(self, context):
        self.recreateOutputs()

    extended = BoolProperty(
        name = "Extended Spline",
        description = "Project point on extended spline. If this is turned on the parameter is not computable.",
        update = settingChanged)

    def create(self):
        self.newInput("Spline", "Spline", "spline", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Vector", "Location", "location")
        self.recreateOutputs()

    @keepNodeState
    def recreateOutputs(self):
        self.outputs.clear()
        self.newOutput("Vector", "Position", "position")
        self.newOutput("Vector", "Tangent", "tangent")
        if not self.extended:
            self.newOutput("Float", "Parameter", "parameter")

    def draw(self, layout):
        layout.prop(self, "extended", text = "Extended")

    def getExecutionCode(self):
        yield "if spline.isEvaluable():"
        if self.extended:
            yield "    position, tangent = spline.projectExtended(location)"
        else:
            yield "    parameter = spline.project(location)"
            yield "    position = spline.evaluate(parameter)"
            yield "    tangent = spline.evaluateTangent(parameter)"
        yield "else:"
        yield "    position = Vector((0, 0, 0))"
        yield "    tangent = Vector((0, 0, 0))"
        yield "    parameter = 0.0"
