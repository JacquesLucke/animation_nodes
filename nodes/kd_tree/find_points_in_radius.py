import bpy
from ... base_types.node import AnimationNode

class FindPointsInRadiusInKDTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindPointsInRadiusInKDTreeNode"
    bl_label = "Find Points in Radius"

    def create(self):
        self.newInput("an_KDTreeSocket", "KDTree", "kdTree")
        socket = self.newInput("an_FloatSocket", "Radius", "radius")
        socket.value = 5
        socket.minValue = 0.0
        self.newInput("an_VectorSocket", "Vector", "searchVector").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("an_VectorListSocket", "Vectors", "nearestVectors")
        self.newOutput("an_FloatListSocket", "Distances", "distances")
        self.newOutput("an_IntegerListSocket", "Indices", "indices")

    def getExecutionCode(self):
        yield "nearestVectors, distances, indices = [], [], []"
        yield "for vector, index, distance in kdTree.find_range(searchVector, max(radius, 0)):"
        yield "    nearestVectors.append(vector)"
        yield "    indices.append(index)"
        yield "    distances.append(distance)"
