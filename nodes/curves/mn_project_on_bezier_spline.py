import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

projectionTypeItems = [
    ("SAMPLED", "Sampled", "Samples a given number of points and outputs the sample/parameter closest to the projecting point"), 
    ("ANALYTIC", "Analytic", "Calculates the projection analytically -- eg, by finding the roots of some higher order numpy.Polynomial")]

class mn_ProjectOnBezierSpline(Node, AnimationNode):
    bl_idname = "mn_ProjectOnBezierSpline"
    bl_label = "Project on Bezier Spline"
    
    resolution = IntProperty(name = "Resolution", default = 100, description = "Amount of samples to find the nearest point", min = 1, update = nodePropertyChanged)
    projectionType = EnumProperty(name = "Projection Type", items = projectionTypeItems, default = "ANALYTIC")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline").showName = False
        self.inputs.new("mn_VectorSocket", "Point")
        self.outputs.new("mn_FloatSocket", "Parameter")
        self.outputs.new("mn_FloatSocket", "Distance")
        self.outputs.new("mn_VectorSocket", "Location")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "projectionType", text = "")
        if self.projectionType == "SAMPLED":
            layout.prop(self, "resolution")

    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Point" : "point"}

    def getOutputSocketNames(self):
        return {"Parameter" : "parameter",
                "Distance" : "distance",
                "Location" : "location"}

    def execute(self, spline, point):
        spline.updateSegments()
        if spline.hasSegments:
            if self.projectionType == "SAMPLED":
                parameter = spline.findNearestSampledParameter(point, self.resolution)
            if self.projectionType == "ANALYTIC":
                parameter = spline.findNearestParameter(point)
            location = spline.evaluate(parameter)
            distance = (point - location).length
            return parameter, distance, location
        else:
            return 0.0, 0.0, Vector((0, 0, 0))