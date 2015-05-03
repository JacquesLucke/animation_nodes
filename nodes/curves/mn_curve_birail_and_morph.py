import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurveBirailAndMorphNode(Node, AnimationNode):
    bl_idname = "mn_CurveBirailAndMorphNode"
    bl_label = "Birail & Morph"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Resolution Along").showName = True
        self.inputs.new("mn_IntegerSocket", "Resolution Across").showName = True
        self.inputs.new("mn_ObjectSocket", "Rail 1").showName = True
        self.inputs.new("mn_ObjectSocket", "Rail 2").showName = True
        self.inputs.new("mn_ObjectSocket", "Begin Profile").showName = True
        self.inputs.new("mn_ObjectSocket", "End Profile").showName = True
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()
    
    def getInputSocketNames(self):
        return {"Resolution Along" : "resAlong",
                "Resolution Across" : "resAcross",
                "Rail 1" : "rail1",
                "Rail 2" : "rail2",
                "Begin Profile" : "beginProfile",
                "End Profile" : "endProfile"}
        
    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}
        
    def canExecute(self, resAlong, resAcross, rail1, rail2, beginProfile, endProfile):
        if resAlong < 2: return False
        if resAcross < 2: return False
        if not Curves.IsBezierCurve(rail1): return False
        if not Curves.IsBezierCurve(rail2): return False
        if not Curves.IsBezierCurve(beginProfile): return False
        if not Curves.IsBezierCurve(endProfile): return False
        
        return True
        
    def execute(self, resAlong, resAcross, rail1, rail2, beginProfile, endProfile):
        vertices = []
        polygons = []
        if not self.canExecute(resAlong, resAcross, rail1, rail2, beginProfile, endProfile):
            return vertices, polygons
        
        try:
            birailedAndMorphedSurface = Surfaces.BirailedAndMorphedSurface(rail1, rail2, beginProfile, endProfile)
            vertices, polygons = birailedAndMorphedSurface.Calculate(resAlong, resAcross)
        except: pass
        
        return vertices, polygons
   
