import bpy
from bpy.types import Node
from mathutils import Vector
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ProjectOnSpline(Node, AnimationNode):
    bl_idname = "mn_ProjectOnSpline"
    bl_label = "Project on Spline"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_FloatSocket", "Parameter")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Location" : "location"}

    def getOutputSocketNames(self):
        return {"Parameter" : "parameter"}

    def execute(self, spline, location):
        spline.update()
        return spline.project(location)
