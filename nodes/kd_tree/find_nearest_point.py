import bpy
from ... base_types.node import AnimationNode

class FindNearestPointInKDTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindNearestPointInKDTreeNode"
    bl_label = "Find Nearest Point"

    def create(self):
        self.newInput("KDTree", "KDTree", "kdTree")
        self.newInput("Vector", "Vector", "searchVector").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("Vector", "Vector", "nearestVector")
        self.newOutput("Float", "Distance", "distance")
        self.newOutput("Integer", "Index", "index")

    def getExecutionCode(self):
        yield "nearestVector, index, distance = kdTree.find(searchVector)"
        yield "if nearestVector is None:"
        yield "    nearestVector, index, distance = Vector((0, 0, 0)), 0.0, -1"
