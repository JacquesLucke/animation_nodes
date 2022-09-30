import bpy
from ... math import Vector
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import (
    Attribute,
    AttributeType,
    AttributeDomain,
    AttributeDataType,
    VirtualVector2DList,
)

class InsertUVMapNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_InsertUVMapNode"
    bl_label = "Insert UV Map"
    errorHandlingType = "EXCEPTION"

    useVector2DList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
        self.newInput("Text", "Name", "uvMapName", value = "AN-UV Map")
        self.newInput(VectorizedSocket("Vector 2D", "useVector2DList",
            ("Position", "position"), ("Positions", "positions")))

        self.newOutput("Mesh", "Mesh", "mesh")

    def execute(self, mesh, uvMapName, positions):
        self.checkAttributeName(mesh, uvMapName)

        positions = VirtualVector2DList.create(positions, Vector((0, 0))).materialize(len(mesh.polygons.indices))
        mesh.insertUVMapAttribute(Attribute(uvMapName, AttributeType.UV_MAP, AttributeDomain.CORNER,
                                            AttributeDataType.FLOAT2, positions))
        return mesh

    def checkAttributeName(self, mesh, attributeName):
        if attributeName == "":
            self.raiseErrorMessage("UV map name can't be empty.")
        elif attributeName in mesh.getAllUVMapAttributeNames():
            self.raiseErrorMessage(f"Mesh has already a uv map with the name '{attributeName}'.")
