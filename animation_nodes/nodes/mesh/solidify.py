import bpy
from ... base_types import AnimationNode
from ... data_structures import VirtualDoubleList
from ... algorithms.meshes.solidify import solidify

class Solidify(bpy.types.Node, AnimationNode):
    bl_idname = "an_SolidifyNode"
    bl_label = "Solidify"
    bl_width_default = 160

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Integer", "Loops", "loops", minValue = 0)
        self.newInput("Float", "Thickness", "thickness")
        self.newInput("Float List", "Offsets", "offsets")
        self.newOutput("Mesh", "Mesh", "outMesh")

    def execute(self, mesh, loops, thickness, offsets):
        offsets = VirtualDoubleList.fromListOrElement(offsets, 0)
        return solidify(mesh, loops, thickness, offsets)
