import bpy
from ... base_types.node import AnimationNode

class FindPointsInRadiusInKDTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindPointsInRadiusInKDTreeNode"
    bl_label = "Find Points in Radius"

    def create(self):
        self.inputs.new("an_KDTreeSocket", "KDTree", "kdTree")
        socket = self.inputs.new("an_FloatSocket", "Radius", "radius")
        socket.value = 5
        socket.minValue = 0.0
        self.inputs.new("an_VectorSocket", "Vector", "searchVector").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_VectorListSocket", "Vectors", "nearestVectors")
        self.outputs.new("an_FloatListSocket", "Distances", "distances")
        self.outputs.new("an_IntegerListSocket", "Indices", "indices")

    def getExecutionCode(self):
        yield "nearestVectors, distances, indices = [], [], []"
        yield "for vector, index, distance in kdTree.find_range(searchVector, max(radius, 0)):"
        yield "    nearestVectors.append(vector)"
        yield "    indices.append(index)"
        yield "    distances.append(distance)"
