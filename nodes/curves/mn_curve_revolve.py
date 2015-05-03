import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurveRevolveNode(Node, AnimationNode):
    bl_idname = "mn_CurveRevolveNode"
    bl_label = "Revolve"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Resolution Along").number = 16
        self.inputs.new("mn_IntegerSocket", "Resolution Across").number = 16
        self.inputs.new("mn_ObjectSocket", "Axis")
        self.inputs.new("mn_ObjectSocket", "Profile")
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()
    
    def getInputSocketNames(self):
        return {"Resolution Along" : "resAlong",
                "Resolution Across" : "resAcross",
                "Axis" : "axis",
                "Profile" : "profile"}
        
    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}
        
    def canExecute(self, resAlong, resAcross, axis, profile):
        if resAlong < 2: return False
        if resAcross < 2: return False
        if not Curves.IsBezierCurve(axis): return False
        if not Curves.IsBezierCurve(profile): return False
        
        return True
        
    def execute(self, resAlong, resAcross, axis, profile):
        vertices = []
        polygons = []
        if not self.canExecute(resAlong, resAcross, axis, profile):
            return vertices, polygons
        
        try:
            revolvedSurface = Surfaces.RevolvedSurface(axis, profile)
            vertices, polygons = revolvedSurface.Calculate(resAlong, resAcross)
        except: pass
        
        return vertices, polygons
   
