import bpy
from ... base_types import AnimationNode
from ... data_structures import DoubleList

class GetUVMapNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetUVMapNode"
    bl_label = "Get UV Map"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Text", "Name", "uvMapName")

        self.newOutput("Float List", "X", "x")
        self.newOutput("Float List", "Y", "y")

    def execute(self, mesh, uvMapName):
        if uvMapName == "":
            self.raiseErrorMessage("UV map name can't be empty.")

        uvMapCos = mesh.getUVMapCos(uvMapName)

        if uvMapCos is None:
            self.raiseErrorMessage(f"Mesh doesn't have a uv map with the name '{uvMapName}'.")

        coList = uvMapCos.asNumpyArray()
        return DoubleList.fromValues(coList[::2]), DoubleList.fromValues(coList[1::2])
