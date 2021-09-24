import bpy
from ... data_structures import DoubleList
from ... base_types import AnimationNode

class GetVertexGroupNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetVertexGroupNode"
    bl_label = "Get Vertex Group"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Text", "Name", "groupName")
        self.newOutput("Float List", "Weights", "weights")

    def execute(self, mesh, attributeName):
        if mesh is None: return None
        if attributeName == "": self.raiseErrorMessage("Attribute name can't be empty.")

        attribute = mesh.getVertexWeightAttribute(attributeName)
        if attribute is None:
            self.raiseErrorMessage(
                    f"mesh does not have attribute with name '{attributeName}'."
                    f"\nAvailable: {mesh.getAllVertexWeightAttributeNames()}"
            )

        return DoubleList.fromValues(attribute.data)
