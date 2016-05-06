import bpy
from ... base_types.node import AnimationNode

class FindNearestNPointsInKDTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindNearestNPointsInKDTreeNode"
    bl_label = "Find Nearest Points"

    def create(self):
        self.newInput("KDTree", "KDTree", "kdTree")
        self.newInput("Integer", "Amount", "amount", value = 5, minValue = 0)
        self.newInput("Vector", "Vector", "searchVector", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Vector List", "Vectors", "nearestVectors")
        self.newOutput("Float List", "Distances", "distances")
        self.newOutput("Integer List", "Indices", "indices")

    def getExecutionCode(self):
        yield "nearestVectors = []"
        yield "distances = DoubleList(allocate = amount)"
        yield "indices = []"
        yield "for vector, index, distance in kdTree.find_n(searchVector, max(amount, 0)):"
        yield "    nearestVectors.append(vector)"
        yield "    indices.append(index)"
        yield "    distances.append(distance)"
