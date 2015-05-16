import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

class mn_ProjectOnBezierSpline(Node, AnimationNode):
    bl_idname = "mn_ProjectOnBezierSpline"
    bl_label = "Project on Bezier Spline"
    
    resolution = bpy.props.IntProperty(name = "Resolution", default = 100, description = "Amount of samples to find the nearest point", min = 1, update = nodePropertyChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline").showName = False
        self.inputs.new("mn_VectorSocket", "Point")
        self.outputs.new("mn_FloatSocket", "Parameter")
        self.outputs.new("mn_VectorSocket", "Location")
        allowCompiling()
        
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "resolution")

    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Point" : "point"}

    def getOutputSocketNames(self):
        return {"Parameter" : "parameter",
                "Location" : "location"}

    def execute(self, spline, point):
        spline.updateSegments()
        if spline.hasSegments:
            parameter = spline.findNearestSampledParameter(point, self.resolution)
            location = spline.evaluate(parameter)
            return parameter, location
        else:
            return 0.0, Vector((0, 0, 0))