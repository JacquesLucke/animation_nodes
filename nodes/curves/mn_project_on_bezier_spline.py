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
    
    def settingsChanged(self, context):
        self.outputs["Parameter"].hide = self.extendSpline and self.projectionType == "ANALYTIC"
        nodePropertyChanged(self, context)
    
    resolution = IntProperty(name = "Resolution", default = 100, description = "Amount of samples to find the nearest point", min = 1, update = nodePropertyChanged)
    projectionType = EnumProperty(name = "Projection Type", items = projectionTypeItems, default = "ANALYTIC", update = settingsChanged)
    extendSpline = BoolProperty(name = "Extend Spline", default = False, update = settingsChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline").showName = False
        self.inputs.new("mn_VectorSocket", "Point")
        self.outputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_VectorSocket", "Tangent")
        self.outputs.new("mn_FloatSocket", "Distance")
        self.outputs.new("mn_FloatSocket", "Parameter")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "projectionType", text = "")
        if self.projectionType == "SAMPLED":
            layout.prop(self, "resolution")
        if self.projectionType == "ANALYTIC":
            layout.prop(self, "extendSpline")

    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Point" : "point"}

    def getOutputSocketNames(self):
        return {"Location" : "location",
                "Tangent" : "tangent",
                "Distance" : "distance",
                "Parameter" : "parameter"}

    def execute(self, spline, point):
        spline.updateSegments()
        if spline.hasSegments:
            if self.projectionType == "ANALYTIC" and self.extendSpline:
                location, tangent = spline.findNearestPointAndTangentExtended(point)
                parameter = 0.0
            else:
                if self.projectionType == "SAMPLED":
                    parameter = spline.findNearestSampledParameter(point, self.resolution)
                if self.projectionType == "ANALYTIC":
                    parameter = spline.findNearestParameter(point)
                location = spline.evaluate(parameter)
                tangent = spline.evaluateTangent(parameter)    
            distance = (point - location).length
            return location, tangent, distance, parameter
        else:
            return Vector((0, 0, 0)), Vector((0, 0, 0)), 0.0, 0.0