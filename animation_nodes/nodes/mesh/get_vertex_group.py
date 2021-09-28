import bpy
from ... data_structures import DoubleList
from ... base_types import AnimationNode

class GetVertexGroupNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetVertexGroupNode"
    bl_label = "Get Vertex Group"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Text", "Name", "vertexWeightName")
        self.newOutput("Float List", "Weights", "weights")

    def execute(self, mesh, vertexWeightName):
        if mesh is None: return None
        if vertexWeightName == "": self.raiseErrorMessage("Vertex group name can't be empty.")

        attribute = mesh.getVertexWeightAttribute(vertexWeightName)
        if attribute is None:
            self.raiseErrorMessage(
                    f"Mesh does not have vertex group with name '{vertexWeightName}'."
                    f"\nAvailable: {mesh.getAllVertexWeightAttributeNames()}"
            )

        return DoubleList.fromValues(attribute.data)
