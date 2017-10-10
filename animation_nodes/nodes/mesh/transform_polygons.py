import bpy
from ... base_types import AnimationNode
from .. matrix.transformation_base_node import MatrixTransformationBase
from . c_utils import transformPolygons, getIndividualPolygonsMesh, extractMeshPolygonTransforms, extractInvertedPolygonTransforms
from ... data_structures import Mesh, EdgeIndicesList

class TransformPolygonsNode(bpy.types.Node, AnimationNode, MatrixTransformationBase):
    bl_idname = "an_TransformPolygonsNode"
    bl_label = "Transform Polygons"
    bl_width_default = 190
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
        newMesh = getIndividualPolygonsMesh(mesh)

        transforms = extractMeshPolygonTransforms(newMesh)
        invertedTransforms = extractInvertedPolygonTransforms(newMesh)
        transformPolygons(newMesh.vertices, newMesh.polygons, invertedTransforms)

        newTransforms = self.transformMatrices(transforms, transformationArgs)

        transformPolygons(newMesh.vertices, newMesh.polygons, newTransforms)
        newMesh.verticesChanged()
        return newMesh

    def transformMatrices(self, matrices, args):
        name = self.getMatrixTransformationFunctionName(useMatrixList = True)
        return getattr(self, name)(matrices, *args)
