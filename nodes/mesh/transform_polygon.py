import bpy
from mathutils import Matrix
from ... base_types.node import AnimationNode

class TransformPolygonNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformPolygonNode"
    bl_label = "Transform Polygon"

    def create(self):
        self.inputs.new("an_PolygonSocket", "Polygon", "polygon").dataIsModified = True
        self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
        self.outputs.new("an_PolygonSocket", "Polygon", "outPolygon")

    def execute(self, polygon, matrix):
        offsetMatrix = Matrix.Translation(polygon.center)
        transfromMatrix = offsetMatrix * matrix * offsetMatrix.inverted()

        for vertex in polygon.vertices:
            vertex.location = transfromMatrix * vertex.location

        return polygon
