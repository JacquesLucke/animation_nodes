import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import (
    FloatList,
    Attribute,
    AttributeType,
    AttributeDomain,
    AttributeDataType,
    VirtualDoubleList,
)

class InsertVertexGroupNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_InsertVertexGroupNode"
    bl_label = "Insert Vertex Group"
    errorHandlingType = "EXCEPTION"

    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
        self.newInput("Text", "Name", "vertexWeightName", value = "AN-Group")
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Weight", "weight"), ("Weights", "weights")))

        self.newOutput("Mesh", "Mesh", "mesh")

    def execute(self, mesh, vertexWeightName, weights):
        self.checkAttributeName(mesh, vertexWeightName)

        weights = FloatList.fromValues(VirtualDoubleList.create(weights, 0).materialize(len(mesh.vertices)))
        mesh.insertVertexWeightAttribute(Attribute(vertexWeightName, AttributeType.VERTEX_WEIGHT,
                                         AttributeDomain.POINT, AttributeDataType.FLOAT, weights))
        return mesh

    def checkAttributeName(self, mesh, attributeName):
        if attributeName == "":
            self.raiseErrorMessage("Vertex group name can't be empty.")
        elif attributeName in mesh.getAllVertexWeightAttributeNames():
            self.raiseErrorMessage(f"Mesh has already a vertex group with the name '{attributeName}'.")
