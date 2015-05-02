import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurveSweepAndMorphNode(Node, AnimationNode):
    bl_idname = "mn_CurveSweepAndMorphNode"
    bl_label = "SweepAndMorph Curves"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Resolution Along").showName = True
        self.inputs.new("mn_IntegerSocket", "Resolution Across").showName = True
        self.inputs.new("mn_ObjectSocket", "Rail").showName = True
        self.inputs.new("mn_ObjectSocket", "BeginProfile").showName = True
        self.inputs.new("mn_ObjectSocket", "EndProfile").showName = True
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()
    
    def getInputSocketNames(self):
        return {"Resolution Along" : "resAlong",
                "Resolution Across" : "resAcross",
                "Rail" : "rail",
                "BeginProfile" : "beginProfile",
                "EndProfile" : "endProfile"}
        
    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}
        
    def canExecute(self, resAlong, resAcross, rail, beginProfile, endProfile):
        if resAlong is None: return False
        if resAcross is None: return False
        if rail is None: return False
        if beginProfile is None: return False
        if endProfile is None: return False
        
        if resAlong < 2: return False
        if resAcross < 2: return False
        if not Curves.IsBezierCurve(rail): return False
        if not Curves.IsBezierCurve(beginProfile): return False
        if not Curves.IsBezierCurve(endProfile): return False
        
        return True
        
    def execute(self, resAlong, resAcross, rail, beginProfile, endProfile):
        vertices = []
        polygons = []
        if not self.canExecute(resAlong, resAcross, rail, beginProfile, endProfile):
            return vertices, polygons
        
        try:
            sweptAndMorphedSurface = Surfaces.SweptAndMorphedSurface(rail, beginProfile, endProfile)
            vertices, polygons = sweptAndMorphedSurface.Calculate(resAlong, resAcross)
        except: pass
        
        return vertices, polygons
   
