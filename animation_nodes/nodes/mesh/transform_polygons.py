import bpy
from bpy.props import *
from mathutils import Matrix
from ... base_types import AnimationNode
from .. matrix.c_utils import getInvertedOrthogonalMatrices
from .. matrix.transformation_base_node import MatrixTransformationBase

from ... data_structures import (
    Mesh, EdgeIndicesList,
    VirtualVector3DList, VirtualMatrix4x4List
)

from . c_utils import (
    matricesFromNormalizedAxisData,
    transformPolygons, getIndividualPolygonsMesh
)

originalTransformTypeItems = [
    ("DEFAULT", "Default", "Use the center as pivot and guess some tangent and bitangent.", "NONE", 0),
    ("CUSTOM_PIVOTS", "Custom Pivots", "Provide custom privots for every polygon. Tangent and bitangent are guessed.", "NONE", 1),
    ("CUSTOM", "Custom", "Provide a transformation matrix for each polygon that represents it. The rotation part of the matrices has to be orthogonal.", "NONE", 2)
]

class TransformPolygonsNode(bpy.types.Node, AnimationNode, MatrixTransformationBase):
    bl_idname = "an_TransformPolygonsNode"
    bl_label = "Transform Polygons"
    bl_width_default = 190
    errorHandlingType = "EXCEPTION"

    originalTransformType = EnumProperty(name = "Original Transform Type", default = "DEFAULT",
        description = "Determines the pivot and rotation axis for each polygon.",
        items = originalTransformTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Mesh", "Mesh", "inMesh")
        self.createMatrixTransformationInputs(useMatrixList = True)

        if self.originalTransformType == "CUSTOM_PIVOTS":
            self.newInput("Vector List", "Pivots", "pivots")
        elif self.originalTransformType == "CUSTOM":
            self.newInput("Matrix List", "Matrices", "matrices")

        self.newOutput("Mesh", "Mesh", "outMesh")

    def draw(self, layout):
        self.draw_MatrixTransformationProperties(layout)

    def drawAdvanced(self, layout):
        layout.prop(self, "originalTransformType", text = "Basis")
        self.drawAdvanced_MatrixTransformationProperties(layout)

    def getExecutionFunctionName(self):
        if self.originalTransformType == "DEFAULT":
            return "execute_Normal"
        elif self.originalTransformType == "CUSTOM_PIVOTS":
            return "execute_CustomPivots"
        elif self.originalTransformType == "CUSTOM":
            return "execute_Custom"

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

    def execute_Custom(self, mesh, *args):
        *transformationArgs, transforms = args
        newMesh = getIndividualPolygonsMesh(mesh)

        transforms = VirtualMatrix4x4List.create(transforms, Matrix()).materialize(len(newMesh.polygons))
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
