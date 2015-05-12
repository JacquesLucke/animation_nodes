import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurveBirailNode(Node, AnimationNode):
    bl_idname = "mn_CurveBirailNode"
    bl_label = "Birail"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Resolution Along").number = Surfaces.defaultResolutionSynthesis
        self.inputs.new("mn_IntegerSocket", "Resolution Across").number = Surfaces.defaultResolutionSynthesis
        self.inputs.new("mn_ObjectSocket", "Rail 1")
        self.inputs.new("mn_ObjectSocket", "Rail 2")
        self.inputs.new("mn_ObjectSocket", "Profile")
        self.inputs.new("mn_ObjectSocket", "End Profile (Optional)")
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Resolution Along" : "resAlong",
                "Resolution Across" : "resAcross",
                "Rail 1" : "rail1",
                "Rail 2" : "rail2",
                "Profile" : "profile",
                "End Profile (Optional)" : "endProfile"}

    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}

    def canExecute(self, resAlong, resAcross, rail1, rail2, profile, endProfile):
        if resAlong < 2: return False
        if resAcross < 2: return False
        if not Curves.IsBezierCurve(rail1): return False
        if not Curves.IsBezierCurve(rail2): return False
        if not Curves.IsBezierCurve(profile): return False

        return True

    def execute(self, resAlong, resAcross, rail1, rail2, profile, endProfile):
        vertices = []
        polygons = []
        if not self.canExecute(resAlong, resAcross, rail1, rail2, profile, endProfile):
            return vertices, polygons

        try:
            if not Curves.IsBezierCurve(endProfile):
                birailedSurface = Surfaces.BirailedSurface(rail1, rail2, profile)
                vertices, polygons = birailedSurface.Calculate(resAlong, resAcross)
            else:
                birailedAndMorphedSurface = Surfaces.BirailedAndMorphedSurface(rail1, rail2, profile, endProfile)
                vertices, polygons = birailedAndMorphedSurface.Calculate(resAlong, resAcross)
        except: pass

        return vertices, polygons
