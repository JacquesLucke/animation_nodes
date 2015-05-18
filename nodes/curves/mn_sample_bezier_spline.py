import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

modeItems = [
    ("PARAMETER", "Parameter Steps", ""),
    ("DISTANCE", "Distance Steps", "")]

class mn_SampleBezierSpline(Node, AnimationNode):
    bl_idname = "mn_SampleBezierSpline"
    bl_label = "Sample Bezier Spline"
    
    def settingChanged(self, context):
        self.inputs["Distance"].hide = self.mode != "DISTANCE"
        self.inputs["Amount"].hide = self.mode != "PARAMETER"
    
    mode = EnumProperty(name = "Mode", items = modeItems, default = "DISTANCE", update = settingChanged)
    resolution = IntProperty(name = "Resolution", description = "Number of samples used to find points with equal distance", default = 100)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline").showName = False
        socket = self.inputs.new("mn_IntegerSocket", "Amount")
        socket.number = 10
        socket.setMinMax(0, 10000000)
        socket = self.inputs.new("mn_FloatSocket", "Distance")
        socket.number = 1
        socket.setMinMax(0, 10000000)
        self.outputs.new("mn_VectorListSocket", "Locations")
        self.settingChanged(context)
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "mode", text = "")
        if self.mode == "DISTANCE":
            layout.prop(self, "resolution")

    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Amount" : "amount",
                "Distance" : "distance"}

    def getOutputSocketNames(self):
        return {"Locations" : "locations"}

    def execute(self, spline, amount, distance):
        spline.updateSegments()
        if spline.hasSegments:
            if self.mode == "DISTANCE":
                return spline.getEqualDistanceSamples(distance, self.resolution)
            if self.mode == "PARAMETER":
                return spline.getSamples(max(amount, 0))
        else:
            return []