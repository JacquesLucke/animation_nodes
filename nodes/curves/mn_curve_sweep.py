import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurveSweepNode(Node, AnimationNode):
    bl_idname = "mn_CurveSweepNode"
    bl_label = "Sweep"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Resolution Along").number = Surfaces.defaultResolutionSynthesis
        self.inputs.new("mn_IntegerSocket", "Resolution Across").number = Surfaces.defaultResolutionSynthesis
        self.inputs.new("mn_ObjectSocket", "Rail")
        self.inputs.new("mn_ObjectSocket", "Profile")
        self.inputs.new("mn_ObjectSocket", "End Profile (Optional)")
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Resolution Along" : "resAlong",
                "Resolution Across" : "resAcross",
                "Rail" : "rail",
                "Profile" : "profile",
                "End Profile (Optional)" : "endProfile"}

    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}

    def canExecute(self, resAlong, resAcross, rail, profile, endProfile):
        if resAlong < 2: return False
        if resAcross < 2: return False
        if not Curves.IsBezierCurve(rail): return False
        if not Curves.IsBezierCurve(profile): return False

        return True

    def execute(self, resAlong, resAcross, rail, profile, endProfile):
        vertices = []
        polygons = []
        if not self.canExecute(resAlong, resAcross, rail, profile, endProfile):
            return vertices, polygons

        try:
            if not Curves.IsBezierCurve(endProfile):
                sweptSurface = Surfaces.SweptSurface(rail, profile)
                vertices, polygons = sweptSurface.Calculate(resAlong, resAcross)
            else:
                sweptAndMorphedSurface = Surfaces.SweptAndMorphedSurface(rail, profile, endProfile)
                vertices, polygons = sweptAndMorphedSurface.Calculate(resAlong, resAcross)
        except: pass

        return vertices, polygons
