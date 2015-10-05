import bpy
from mathutils import Vector
from ... base_types.node import AnimationNode

class FindNearestNPointsInKDTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindNearestNPointsInKDTreeNode"
    bl_label = "Find Nearest Points"

    def create(self):
        self.inputs.new("an_KDTreeSocket", "KDTree", "kdTree")
        self.inputs.new("an_IntegerSocket", "Amount", "amount").value = 5
        self.inputs.new("an_VectorSocket", "Vector", "searchVector").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_VectorListSocket", "Vectors", "nearestVectors")
        self.outputs.new("an_FloatListSocket", "Distances", "distances")
        self.outputs.new("an_IntegerListSocket", "Indices", "indices")

    def getExecutionCode(self):
        yield "nearestVectors, distances, indices = [], [], []"
        yield "for vector, index, distance in kdTree.find_n(searchVector, amount):"
        yield "    nearestVectors.append(vector)"
        yield "    indices.append(index)"
        yield "    distances.append(distance)"
