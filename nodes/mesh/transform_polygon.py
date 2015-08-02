import bpy
from mathutils import Matrix
from ... base_types.node import AnimationNode

class TransformPolygon(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TransformPolygon"
    bl_label = "Transform Polygon"

    inputNames = { "Polygon" : "polygon",
                   "Matrix" : "matrix" }

    outputNames = { "Polygon" : "polygon" }

    def create(self):
        self.inputs.new("mn_PolygonSocket", "Polygon")
        self.inputs.new("mn_MatrixSocket", "Matrix")
        self.outputs.new("mn_PolygonSocket", "Polygon")

    def execute(self, polygon, matrix):
        offsetMatrix = Matrix.Translation(polygon.center)
        transfromMatrix = offsetMatrix * matrix * offsetMatrix.inverted()

        for vertex in polygon.vertices:
            vertex.location = transfromMatrix * vertex.location

        return polygon
