import bpy
from mathutils.kdtree import KDTree
from ... base_types.node import AnimationNode

class FindCloseVertices(bpy.types.Node, AnimationNode):
    bl_idname = "mn_FindCloseVertices"
    bl_label = "Find Close Vertices"

    inputNames = { "Vertices" : "vertices",
                   "Clusters" : "clusters",
                   "Connections" : "connections",
                   "Min Distance" : "minDistance",
                   "Max Distance" : "maxDistance" }

    outputNames = { "Edges" : "edges" }

    def create(self):
        self.inputs.new("mn_VectorListSocket", "Vertices")
        self.inputs.new("mn_IntegerSocket", "Clusters").value = 1000
        self.inputs.new("mn_IntegerSocket", "Connections").value = 3
        self.inputs.new("mn_FloatSocket", "Min Distance").value = 0.02
        self.inputs.new("mn_FloatSocket", "Max Distance").value = 0.3
        self.outputs.new("mn_EdgeIndicesListSocket", "Edges")

    def execute(self, vertices, clusters, connections, minDistance, maxDistance):
        minDistance = max(0, minDistance)
        maxDistance = max(minDistance, maxDistance)

        verticesAmount = len(vertices)
        kdTree = KDTree(verticesAmount)
        for i, vector in enumerate(vertices):
            kdTree.insert(vector, i)
        kdTree.balance()
        edges = []
        for searchIndex in range(min(verticesAmount, clusters)):
            added = 0
            for (vector, foundIndex, distance) in kdTree.find_range(vertices[searchIndex], maxDistance):
                if searchIndex != foundIndex and distance > minDistance:
                    if added >= connections: break
                    if foundIndex > searchIndex:
                        edge = (searchIndex, foundIndex)
                    else:
                        edge = (foundIndex, searchIndex)
                    edges.append(edge)
                    added += 1
                    
        return list(set(edges))
