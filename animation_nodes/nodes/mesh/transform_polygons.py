import bpy
from bpy.props import *
from ... base_types import AnimationNode
from .. matrix.c_utils import getInvertedOrthogonalMatrices
from .. matrix.transformation_base_node import MatrixTransformationBase
from ... data_structures import Mesh, EdgeIndicesList, VirtualVector3DList
from . c_utils import transformPolygons, matricesFromNormalizedAxisData, getIndividualPolygonsMesh

class TransformPolygonsNode(bpy.types.Node, AnimationNode, MatrixTransformationBase):
    bl_idname = "an_TransformPolygonsNode"
    bl_label = "Transform Polygons"
    bl_width_default = 190
    errorHandlingType = "EXCEPTION"

    useCustomPivots = BoolProperty(name = "Use Custom Pivots", default = False,
        description = "Tell the node a pivot of each polygon.",
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("Mesh", "Mesh", "inMesh")
        self.createMatrixTransformationInputs(useMatrixList = True)
        if self.useCustomPivots:
            self.newInput("Vector List", "Pivots", "pivots")
        self.newOutput("Mesh", "Mesh", "outMesh")

    def draw(self, layout):
        self.draw_MatrixTransformationProperties(layout)

    def drawAdvanced(self, layout):
        layout.prop(self, "useCustomPivots")
        self.drawAdvanced_MatrixTransformationProperties(layout)

    def getExecutionFunctionName(self):
        if self.useCustomPivots:
            return "execute_CustomPivots"
        else:
            return "execute_Normal"

    def execute_Normal(self, mesh, *transformationArgs):
        newMesh = getIndividualPolygonsMesh(mesh)
        centers = newMesh.getPolygonCenters()
        normals, tangents, bitangents = newMesh.getPolygonOrientationMatrices(normalized = True)
        transforms = matricesFromNormalizedAxisData(centers, tangents, bitangents, normals)
        return self.transformMeshPolygons(newMesh, transforms, transformationArgs)

    def execute_CustomPivots(self, mesh, *args):
        *transformationArgs, pivots = args

        newMesh = getIndividualPolygonsMesh(mesh)
        pivots = VirtualVector3DList.create(pivots, (0, 0, 0)).materialize(len(newMesh.polygons))
        normals, tangents, bitangents = newMesh.getPolygonOrientationMatrices(normalized = True)
        transforms = matricesFromNormalizedAxisData(pivots, tangents, bitangents, normals)
        return self.transformMeshPolygons(newMesh, transforms, transformationArgs)

    def transformMeshPolygons(self, mesh, transforms, transformationArgs):
        invertedTransforms = getInvertedOrthogonalMatrices(transforms)

        transformPolygons(mesh.vertices, mesh.polygons, invertedTransforms)
        newTransforms = self.transformMatrices(transforms, transformationArgs)
        transformPolygons(mesh.vertices, mesh.polygons, newTransforms)
        mesh.verticesChanged()

        return mesh

    def transformMatrices(self, matrices, args):
        name = self.getMatrixTransformationFunctionName(useMatrixList = True)
        return getattr(self, name)(matrices, *args)
