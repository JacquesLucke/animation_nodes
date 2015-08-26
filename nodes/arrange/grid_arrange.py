import bpy
from mathutils import Vector
from ... base_types.node import AnimationNode

class GridArrangeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GridArrangeNode"
    bl_label = "Grid Arrange"

    def create(self):
        self.inputs.new("an_IntegerSocket", "Index", "index")
        self.inputs.new("an_IntegerSocket", "Width", "width").value = 10
        self.inputs.new("an_FloatSocket", "Distance", "distance").value = 3
        self.outputs.new("an_VectorSocket", "Vector", "vector")

    def execute(self, index, width, distance):
        width = max(width, 1)
        vector = Vector((0, 0, 0))
        vector.x = index % width * distance
        vector.y = int(index / width) * distance
        return vector
