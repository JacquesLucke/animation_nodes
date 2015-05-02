import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurveBirailAndMorphNode(Node, AnimationNode):
    bl_idname = "mn_CurveBirailAndMorphNode"
    bl_label = "BirailAndMorph Curves"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Resolution Along").showName = True
        self.inputs.new("mn_IntegerSocket", "Resolution Across").showName = True
        self.inputs.new("mn_ObjectSocket", "Rail1").showName = True
        self.inputs.new("mn_ObjectSocket", "Rail2").showName = True
        self.inputs.new("mn_ObjectSocket", "BeginProfile").showName = True
        self.inputs.new("mn_ObjectSocket", "EndProfile").showName = True
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()
    
    def getInputSocketNames(self):
        return {"Resolution Along" : "resAlong",
                "Resolution Across" : "resAcross",
                "Rail1" : "rail1",
                "Rail2" : "rail2",
                "BeginProfile" : "beginProfile",
                "EndProfile" : "endProfile"}
        
    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}
        
    def execute(self, resAlong, resAcross, rail1, rail2, beginProfile, endProfile):
        birailedAndMorphedSurface = Surfaces.BirailedAndMorphedSurface(rail1, rail2, beginProfile, endProfile)
        vertices, polygons = birailedAndMorphedSurface.Calculate(resAlong, resAcross)
        
        return vertices, polygons
   
