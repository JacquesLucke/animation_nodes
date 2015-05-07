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
        self.inputs["Resolution Projection"].hide = (self.mode == "Fast")
    
    def modeChanged(self, context):
        self.updateSocketVisibility()
        nodeTreeChanged()
    
    modes = ["Fast", "Projected"]
    modes_items = [(t, t, "") for t in modes]
    mode = bpy.props.EnumProperty(name = "Mode", items = modes_items, default = "Fast", update = modeChanged)
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "mode")

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Resolution Along").number = 16
        self.inputs.new("mn_IntegerSocket", "Resolution Across").number = 16
        self.inputs.new("mn_IntegerSocket", "Resolution Projection").number = 64
        self.inputs.new("mn_ObjectSocket", "Axis")
        self.inputs.new("mn_ObjectSocket", "Profile")
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Resolution Along" : "resAlong",
                "Resolution Across" : "resAcross",
                "Resolution Projection" : "resProjection",
                "Axis" : "axis",
                "Profile" : "profile"}

    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}

    def canExecute(self, resAlong, resAcross, resProjection, axis, profile):
        if resAlong < 2: return False
        if resAcross < 2: return False
        if self.mode == "Projected":
            if resProjection < 2: return False
        if not Curves.IsBezierCurve(axis): return False
        if not Curves.IsBezierCurve(profile): return False

        return True

    def execute(self, resAlong, resAcross, resProjection, axis, profile):
        vertices = []
        polygons = []
        if not self.canExecute(resAlong, resAcross, resProjection, axis, profile):
            return vertices, polygons

        try:
            if self.mode == "Fast":
                revolvedSurface = Surfaces.RevolvedSurface(axis, profile)
                vertices, polygons = revolvedSurface.Calculate(resAlong, resAcross)
                return vertices, polygons
            if self.mode == "Projected":
                revolvedProjectedSurface = Surfaces.RevolvedProjectedSurface(axis, profile)
                vertices, polygons = revolvedProjectedSurface.Calculate(resAlong, resAcross, resProjection)
        except: pass

        return vertices, polygons
