import bpy
from ... base_types import AnimationNode
from .. matrix.transformation_base_node import MatrixTransformationBase
from . c_utils import transformPolygons, separatePolygons, extractPolygonTransforms
from ... data_structures import Mesh, EdgeIndicesList
from ... data_structures.meshes.mesh_data import createValidEdgesList

class TransformPolygonsNode(bpy.types.Node, AnimationNode, MatrixTransformationBase):
    bl_idname = "an_TransformPolygonsNode"
    bl_label = "Transform Polygons"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "inMesh")
        self.createMatrixTransformationInputs(useMatrixList = True)
        self.newOutput("Mesh", "Mesh", "outMesh")

    def draw(self, layout):
        self.draw_MatrixTransformationProperties(layout)

    def drawAdvanced(self, layout):
        self.drawAdvanced_MatrixTransformationProperties(layout)

    def execute(self, mesh, *transformationArgs):
        newVertices, newPolygons = separatePolygons(mesh.vertices, mesh.polygons)
        transforms, invertedTransforms = extractPolygonTransforms(newVertices, newPolygons, calcInverted = True)
        transformPolygons(newVertices, newPolygons, invertedTransforms)
        newTransforms = self.transformMatrices(transforms, transformationArgs)
        transformPolygons(newVertices, newPolygons, newTransforms)
        newEdges = createValidEdgesList(EdgeIndicesList(), newPolygons)
        return Mesh(newVertices, newEdges, newPolygons)

    def transformMatrices(self, matrices, args):
        name = self.getMatrixTransformationFunctionName(useMatrixList = True)
        return getattr(self, name)(matrices, *args)
