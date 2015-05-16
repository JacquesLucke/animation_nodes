import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

class mn_BezierSplineInfo(Node, AnimationNode):
    bl_idname = "mn_BezierSplineInfo"
    bl_label = "Bezier Spline Info"
    
    resolution = bpy.props.IntProperty(default = 5, name = "Resolution", description = "Samples per spline segment to calculate the length.", update = nodePropertyChanged, min = 1)

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline").showName = False
        self.outputs.new("mn_BezierPointListSocket", "Points")
        self.outputs.new("mn_FloatSocket", "Length")
        allowCompiling()
        
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "resolution")

    def getInputSocketNames(self):
        return {"Spline" : "spline"}

    def getOutputSocketNames(self):
        return {"Points" : "points",
                "Length" : "length"}

    def execute(self, spline):
        spline.updateSegments()
        return spline.points, spline.calculateLength(self.resolution)
