import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.mesh import *
from mathutils import Matrix

class mn_TransformPolygon(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TransformPolygon"
    bl_label = "Transform Polygon"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_PolygonSocket", "Polygon")
        self.inputs.new("mn_MatrixSocket", "Matrix")
        self.outputs.new("mn_PolygonSocket", "Polygon")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Polygon" : "polygon",
                "Matrix" : "matrix"}
    def getOutputSocketNames(self):
        return {"Polygon" : "polygon"}

    def execute(self, polygon, matrix):
        offsetMatrix = Matrix.Translation(polygon.center)
        transfromMatrix = offsetMatrix * matrix * offsetMatrix.inverted()

        for vertex in polygon.vertices:
            vertex.location = transfromMatrix * vertex.location

        return polygon
