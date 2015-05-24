import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... algorithms.mesh_generation.from_splines import loftSplines

class mn_LoftSplines(Node, AnimationNode):
    bl_idname = "mn_LoftSplines"
    bl_label = "Loft Splines"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineListSocket", "Splines")
        self.inputs.new("mn_IntegerSocket", "Spline Samples")
        self.inputs.new("mn_IntegerSocket", "Surface Samples")
        self.outputs.new("mn_VectorListSocket", "Vertices")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygons")
        self.width += 20
        allowCompiling()

    def getInputSocketNames(self):
        return {"Splines" : "splines",
                "Spline Samples" : "splineSamples",
                "Surface Samples" : "surfaceSamples"}

    def getOutputSocketNames(self):
        return {"Vertices" : "vertices",
                "Polygons" : "polygons"}

    def execute(self, splines, splineSamples, surfaceSamples):
        for spline in splines:
            spline.update()
            
        return loftSplines(splines, splineSamples, surfaceSamples)
