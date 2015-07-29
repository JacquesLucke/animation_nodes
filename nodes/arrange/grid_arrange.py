import bpy
from mathutils import Vector
from ... base_types.node import AnimationNode

class GridArrange(bpy.types.Node, AnimationNode):
    bl_idname = "mn_GridArrange"
    bl_label = "Grid Arrange"
    isDetermined = True
    
    def create(self):
        self.inputs.new("mn_IntegerSocket", "Index")
        self.inputs.new("mn_IntegerSocket", "Width").value = 10
        self.inputs.new("mn_FloatSocket", "Distance").value = 3
        self.outputs.new("mn_VectorSocket", "Vector")
        
    def getInputSocketNames(self):
        return {"Index" : "index",
                "Width" : "width",
                "Distance" : "distance"}
                
    def getOutputSocketNames(self):
        return {"Vector" : "vector"}

    def execute(self, index, width, distance):
        width = max(width, 1)
        vector = Vector((0, 0, 0))
        vector.x = index % width * distance
        vector.y = int(index / width) * distance
        return vector