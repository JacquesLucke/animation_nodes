import bpy
from ... base_types import AnimationNode
from ... data_structures import AttributeType

class GetUVMapNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetUVMapNode"
    bl_label = "Get UV Map"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Text", "Name", "uvMapName")

        self.newOutput("Vector 2D List", "Positions", "positions")

    def execute(self, mesh, uvMapName):
        if uvMapName == "":
            self.raiseErrorMessage("UV map name can't be empty.")

        uvMap = mesh.getAttribute(uvMapName, AttributeType.UV_MAP)
        if uvMap is None:
            self.raiseErrorMessage(f"Mesh doesn't have a uv map with the name '{uvMapName}'.")

        return uvMap.data
