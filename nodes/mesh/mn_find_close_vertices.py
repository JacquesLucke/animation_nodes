import bpy
from bpy.types import Node
from mathutils.kdtree import KDTree
from ... mn_node_base import AnimationNode
from ... mn_execution import allowCompiling, forbidCompiling

class mn_FindCloseVertices(Node, AnimationNode):
    bl_idname = "mn_FindCloseVertices"
    bl_label = "Find Close Vertices"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorListSocket", "Vertices")
        self.inputs.new("mn_IntegerSocket", "Clusters").number = 1000
        self.inputs.new("mn_IntegerSocket", "Connections").number = 3
        self.inputs.new("mn_FloatSocket", "Min Distance").number = 0.02
        self.inputs.new("mn_FloatSocket", "Max Distance").number = 0.3
        self.outputs.new("mn_EdgeIndicesListSocket", "Edges")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Vertices" : "vertices",
                "Clusters" : "clusters",
                "Connections" : "connections",
                "Min Distance" : "minDistance",
                "Max Distance" : "maxDistance"}
    def getOutputSocketNames(self):
        return {"Edges" : "edges"}
        
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