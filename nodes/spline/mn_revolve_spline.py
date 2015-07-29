import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... algorithms.mesh_generation.from_splines import revolveProfileAroundAxis

projectionTypeItems = [
    ("PARAMETER", "Same Parameter", ""),
    ("PROJECT", "Project", "") ]

class mn_RevolveSpline(bpy.types.Node, AnimationNode):
    bl_idname = "mn_RevolveSpline"
    bl_label = "Revolve Spline"
        
    projectionType = EnumProperty(name = "Projection Type", default = "PROJECT", items = projectionTypeItems, update = nodePropertyChanged)
        
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Axis")
        self.inputs.new("mn_SplineSocket", "Profile")
        socket = self.inputs.new("mn_IntegerSocket", "Spline Samples")
        socket.setMinMax(2, 10000)
        socket.number = 16
        socket = self.inputs.new("mn_IntegerSocket", "Surface Samples")
        socket.setMinMax(3, 10000)
        socket.number = 16
        self.outputs.new("mn_VectorListSocket", "Vertices")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygons")
        self.width += 20
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "projectionType", text = "")

    def getInputSocketNames(self):
        return {"Axis" : "axis",
                "Profile" : "profile",
                "Spline Samples" : "splineSamples",
                "Surface Samples" : "surfaceSamples"}

    def getOutputSocketNames(self):
        return {"Vertices" : "vertices",
                "Polygons" : "polygons"}

    def execute(self, axis, profile, splineSamples, surfaceSamples):
        def canExecute():
            if not axis.isEvaluable: return False
            if not profile.isEvaluable: return False
            if splineSamples < 2: return False
            if surfaceSamples < 3: return False
            return True
            
        axis.update()
        profile.update()
        
        if canExecute():
            vertices, polygons = revolveProfileAroundAxis(axis, profile, splineSamples, surfaceSamples, self.projectionType)
            return vertices, polygons
        else: return [], []
