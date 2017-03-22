import bpy
from mathutils.kdtree import KDTree
from ... base_types import AnimationNode
from ... data_structures import EdgeIndicesList

class FindClosePointsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindClosePointsNode"
    bl_label = "Find Close Points"

    def create(self):
        self.newInput("Vector List", "Points", "points")
        self.newInput("Integer", "Clusters", "clusters", value = 1000)
        self.newInput("Integer", "Connections", "connections", value = 3)
        self.newInput("Float", "Min Distance", "minDistance", value = 0.02)
        self.newInput("Float", "Max Distance", "maxDistance", value = 0.3)
        self.newOutput("Edge Indices List", "Edges", "edges")

    def execute(self, points, clusters, connections, minDistance, maxDistance):
        minDistance = max(0, minDistance)
        maxDistance = max(minDistance, maxDistance)

        verticesAmount = len(points)
        kdTree = KDTree(verticesAmount)
        for i, vector in enumerate(points):
            kdTree.insert(vector, i)
        kdTree.balance()
        edges = []
        for searchIndex in range(min(verticesAmount, clusters)):
            added = 0
            for (vector, foundIndex, distance) in kdTree.find_range(points[searchIndex], maxDistance):
                if searchIndex != foundIndex and distance > minDistance:
                    if added >= connections: break
                    if foundIndex > searchIndex:
                        edge = (searchIndex, foundIndex)
                    else:
                        edge = (foundIndex, searchIndex)
                    edges.append(edge)
                    added += 1

        return EdgeIndicesList.fromValues(tuple(set(edges)))
