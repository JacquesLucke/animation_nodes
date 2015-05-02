import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurveSweepNode(Node, AnimationNode):
    bl_idname = "mn_CurveSweepNode"
    bl_label = "Sweep Curves"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Resolution Along").showName = True
        self.inputs.new("mn_IntegerSocket", "Resolution Across").showName = True
        self.inputs.new("mn_ObjectSocket", "Rail").showName = True
        self.inputs.new("mn_ObjectSocket", "Profile").showName = True
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()
    
    def getInputSocketNames(self):
        return {"Resolution Along" : "resAlong",
                "Resolution Across" : "resAcross",
                "Rail" : "rail",
                "Profile" : "profile"}
        
    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}
        
    def canExecute(self, resAlong, resAcross, rail, profile):
        if resAlong is None: return False
        if resAcross is None: return False
        if rail is None: return False
        if profile is None: return False
        
        if resAlong < 2: return False
        if resAcross < 2: return False
        if not Curves.IsBezierCurve(rail): return False
        if not Curves.IsBezierCurve(profile): return False
        
        return True
        
    def execute(self, resAlong, resAcross, rail, profile):
        vertices = []
        polygons = []
        if not self.canExecute(resAlong, resAcross, rail, profile):
            return vertices, polygons
        
        try:
            sweptSurface = Surfaces.SweptSurface(rail, profile)
            vertices, polygons = sweptSurface.Calculate(resAlong, resAcross)
        except: pass
        
        return vertices, polygons
   
