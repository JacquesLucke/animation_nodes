import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces


class mn_CurveRevolveNode(Node, AnimationNode):
    bl_idname = "mn_CurveRevolveNode"
    bl_label = "Revolve"
        
    def updateSocketVisibility(self):
        self.inputs["Resolution Projection"].hide = not ((self.mode == "Project Profile") and (self.projection_mode == "Sampled"))
    
    def modeChanged(self, context):
        self.updateSocketVisibility()
        nodeTreeChanged()
    
    modes_items = [ ("Same Parameter", "Same Parameter", "Uses the same parameter to calculate points on the Axis & Profile. May be fast, but might look weird."),
                    ("Project Profile", "Project Profile", "Projects sampled points on the Profile onto the Axis. May take longer, but probably looks better.")]
    mode = bpy.props.EnumProperty(name = "Mode", items = modes_items, default = "Project Profile", update = modeChanged)
    projection_modes_items = [ ("Sampled", "Sampled", "Samples a given number of points and outputs the sample/parameter closest to the projecting point"), 
                               ("Analytic", "Analytic", "WIP. Calculates the projection analytically -- eg, by finding the roots of some higher order numpy.Polynomial")]
    projection_mode = bpy.props.EnumProperty(name = "Projection Mode", items = projection_modes_items, default = "Analytic", update = modeChanged)
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "mode")
        if self.mode == "Project Profile": layout.prop(self, "projection_mode")

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Resolution Projection").number = Curves.defaultResolutionAnalysis
        self.inputs.new("mn_IntegerSocket", "Resolution Along").number = Surfaces.defaultResolutionSynthesis
        self.inputs.new("mn_IntegerSocket", "Resolution Across").number = Surfaces.defaultResolutionSynthesis
        self.inputs.new("mn_ObjectSocket", "Axis")
        self.inputs.new("mn_ObjectSocket", "Profile")
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Resolution Projection" : "resProjection",
                "Resolution Along" : "resAlong",
                "Resolution Across" : "resAcross",
                "Axis" : "axis",
                "Profile" : "profile"}

    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}

    def canExecute(self, resProjection, resAlong, resAcross, axis, profile):
        if resAlong < 2: return False
        if resAcross < 2: return False
        if self.mode == "Project Profile":
            if self.projection_mode == "Sampled":
                if resProjection < 2: return False
        if not Curves.IsBezierCurve(axis): return False
        if not Curves.IsBezierCurve(profile): return False

        return True

    def execute(self, resProjection, resAlong, resAcross, axis, profile):
        vertices = []
        polygons = []
        if not self.canExecute(resProjection, resAlong, resAcross, axis, profile):
            return vertices, polygons

        try:
            if self.mode == "Same Parameter":
                revolvedSurface = Surfaces.RevolvedSurface(axis, profile)
                vertices, polygons = revolvedSurface.Calculate(resAlong, resAcross)
                return vertices, polygons
            if self.mode == "Project Profile":
                if self.projection_mode == "Sampled":
                    revolvedProjectedSurface = Surfaces.RevolvedProjectedSurface(axis, profile)
                    vertices, polygons = revolvedProjectedSurface.Calculate(resAlong, resAcross, resProjection)
                    return vertices, polygons
                if self.projection_mode == "Analytic":
                    revolvedProjectedSurface = Surfaces.RevolvedProjectedSurface(axis, profile)
                    vertices, polygons = revolvedProjectedSurface.CalculateAnalytic(resAlong, resAcross)
        except: pass
        
        return vertices, polygons
