import bpy
from bpy.props import *
from ... base_types import AnimationNode
from . c_utils import replicateMesh

transformationTypeItems = [
    ("Matrix List", "Matrices", "", "NONE", 0),
    ("Vector List", "Vectors", "", "NONE", 1)
]

class ReplicateMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplicateMeshNode"
    bl_label = "Replicate Mesh"

    transformationType = EnumProperty(name = "Transformation Type", default = "Matrix List",
        items = transformationTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Mesh", "Mesh", "sourceMesh")
        self.newInput(self.transformationType, "Transformations", "transformations")
        self.newOutput("Mesh", "Mesh", "outMesh")

    def draw(self, layout):
        layout.prop(self, "transformationType", text = "")

    def execute(self, source, transformations):
        return replicateMesh(source, transformations)
