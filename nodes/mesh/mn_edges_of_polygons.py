import bpy
from bpy.types import Node
from mathutils import Vector
from ... mn_node_base import AnimationNode
from ... mn_execution import allowCompiling, forbidCompiling, nodePropertyChanged

class mn_EdgesOfPolygons(Node, AnimationNode):
    bl_idname = "mn_EdgesOfPolygons"
    bl_label = "Edges of Polygons"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_PolygonIndicesListSocket", "Polygons")
        self.outputs.new("mn_EdgeIndicesListSocket", "Edges")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Polygons" : "polygons"}
    def getOutputSocketNames(self):
        return {"Edges" : "edges"}
        
    def execute(self, polygons):
        edges = []
        for polygon in polygons:
            for i, index in enumerate(polygon):
                startIndex = polygon[i - 1]
                edge = (startIndex, index) if index > startIndex else (index, startIndex)
                edges.append(edge)
        return list(set(edges))