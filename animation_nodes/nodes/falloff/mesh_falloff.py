import bpy
from bpy.props import *
from mathutils.bvhtree import BVHTree
from ... events import propertyChanged
from ... base_types import AnimationNode
from . mesh_falloff_utils import calculateMeshSurfaceFalloff, calculateMeshVolumeFalloff

modeItems = [
    ("SURFACE", "Surface", "Falloff w.r.t mesh surface", "NONE", 0),
    ("VOLUME", "Volume", "Falloff w.r.t mesh volume", "NONE", 1)
]

class MeshFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshFalloffNode"
    bl_label = "Mesh Falloff"
    errorHandlingType = "EXCEPTION"

    mode: EnumProperty(name = "Mode", default = "SURFACE",
        items = modeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        if self.mode == "SURFACE":
            self.newInput("Float", "Size", "size")
            self.newInput("Float", "Falloff Width", "falloffWidth", value = 1)
            self.newInput("Boolean", "Use Volume", "useVolume", value = False)
            self.newInput("Boolean", "Invert", "invert", value = False)
            self.newInput("Float", "Max Distance", "bvhMaxDistance", minValue = 0, value = 1e6, hide = True)
            self.newInput("Float", "Epsilon", "epsilon", minValue = 0, hide = True)
        else:
            self.newInput("Boolean", "Invert", "invert", value = False)
            self.newInput("Float", "Epsilon", "epsilon", minValue = 0, hide = True)

        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def getExecutionFunctionName(self):
        if self.mode == "SURFACE":
            return "execute_MeshSurfaceFalloff"
        elif self.mode == "VOLUME":
            return "execute_MeshVolumeFalloff"

    def execute_MeshSurfaceFalloff(self, mesh, size, falloffWidth, useVolume, invert, bvhMaxDistance, epsilon):
        vectorList, polygonsIndices = self.validMesh(mesh)
        bvhTree = BVHTree.FromPolygons(vectorList, polygonsIndices, epsilon = max(epsilon, 0))
        return calculateMeshSurfaceFalloff(bvhTree, bvhMaxDistance, size, falloffWidth, useVolume, invert)

    def execute_MeshVolumeFalloff(self, mesh, invert, epsilon):
        vectorList, polygonsIndices = self.validMesh(mesh)
        bvhTree = BVHTree.FromPolygons(vectorList, polygonsIndices, epsilon = max(epsilon, 0))
        return calculateMeshVolumeFalloff(bvhTree, invert)

    def validMesh(self, mesh):
        vectorList = mesh.vertices
        if len(vectorList) == 0:
            self.raiseErrorMessage("Invalid Mesh.")

        polygonsIndices = mesh.polygons
        if len(polygonsIndices.indices) == 0:
            self.raiseErrorMessage("Invalid Mesh.")

        return vectorList, polygonsIndices
