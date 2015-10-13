import bpy
from bpy.props import *
from ... events import executionCodeChanged
from mathutils import Vector
from ... base_types.node import AnimationNode

class ObjectBoundingBoxNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectBoundingBoxNode"
    bl_label = "Object Bounding Box"
    
    useWorldSpace = BoolProperty(name = "Use World Space", default = True,
        update = executionCodeChanged)
    
    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_VectorListSocket", "Vertices", "vertices")
        self.outputs.new("an_EdgeIndicesListSocket", "Edges", "edges")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygons", "polygons")
        
    def drawAdvanced(self, layout):
        layout.prop(self, "useWorldSpace")
    
    def execute(self, object):
        if object is not None:
            if self.useWorldSpace:
                matrix = object.matrix_world
                vertices = [matrix * Vector(v) for v in object.bound_box]
            else: vertices = [Vector(v) for v in object.bound_box]
            edges = [(0, 1), (1, 2), (2, 3), (0, 3), (4, 5), (5, 6), (6, 7), (4, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
            polygons = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 3, 7, 4), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6)]
            return vertices, edges, polygons
        return [], [], []
