import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurveLoftNode(Node, AnimationNode):
    bl_idname = "mn_CurveLoftNode"
    bl_label = "Loft Curves"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Resolution Along").showName = True
        self.inputs.new("mn_IntegerSocket", "Resolution Across").showName = True
        self.inputs.new("mn_ObjectSocket", "Rail1").showName = True
        self.inputs.new("mn_ObjectSocket", "Rail2").showName = True
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Resolution Along" : "resAlong",
                "Resolution Across" : "resAcross",
                "Rail1" : "rail1",
                "Rail2" : "rail2"}
        
    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}
        
    def canExecute(self, resAlong, resAcross, rail1, rail2):
        if resAlong is None: return False
        if resAcross is None: return False
        if rail1 is None: return False
        if rail2 is None: return False
        
        if resAlong < 2: return False
        if resAcross < 2: return False
        if not Curves.IsBezierCurve(rail1): return False
        if not Curves.IsBezierCurve(rail2): return False
        
        return True
        
    def execute(self, resAlong, resAcross, rail1, rail2):
        vertices = []
        polygons = []
        if not self.canExecute(resAlong, resAcross, rail1, rail2):
            return vertices, polygons
        
        try:
            loftedSurface = Surfaces.LoftedSurface(rail1, rail2)
            vertices, polygons = loftedSurface.Calculate(resAlong, resAcross)
        except: pass
        
        return vertices, polygons
   
