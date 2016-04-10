import bpy
from ... base_types.node import AnimationNode

class FindNearestNPointsInKDTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindNearestNPointsInKDTreeNode"
    bl_label = "Find Nearest Points"

    def create(self):
        self.newInput("an_KDTreeSocket", "KDTree", "kdTree")
        self.newInput("an_IntegerSocket", "Amount", "amount").value = 5
        self.newInput("an_VectorSocket", "Vector", "searchVector").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("an_VectorListSocket", "Vectors", "nearestVectors")
        self.newOutput("an_FloatListSocket", "Distances", "distances")
        self.newOutput("an_IntegerListSocket", "Indices", "indices")

    def getExecutionCode(self):
        yield "nearestVectors, distances, indices = [], [], []"
        yield "for vector, index, distance in kdTree.find_n(searchVector, amount):"
        yield "    nearestVectors.append(vector)"
        yield "    indices.append(index)"
        yield "    distances.append(distance)"
