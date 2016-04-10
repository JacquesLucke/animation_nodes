import bpy
from mathutils.kdtree import KDTree
from ... base_types.node import AnimationNode

class FindCloseVerticesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindCloseVerticesNode"
    bl_label = "Find Close Vertices"

    def create(self):
        self.newInput("an_VectorListSocket", "Vertices", "vertices")
        self.newInput("an_IntegerSocket", "Clusters", "clusters").value = 1000
        self.newInput("an_IntegerSocket", "Connections", "connections").value = 3
        self.newInput("an_FloatSocket", "Min Distance", "minDistance").value = 0.02
        self.newInput("an_FloatSocket", "Max Distance", "maxDistance").value = 0.3
        self.newOutput("an_EdgeIndicesListSocket", "Edges", "edges")

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
