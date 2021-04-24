import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures import (
    Mesh,
    LongList,
    Attribute,
    AttributeType,
    AttributeDomain,
    AttributeDataType,
)

class CombineMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineMeshNode"
    bl_label = "Combine Mesh"
    errorHandlingType = "EXCEPTION"

    skipValidation: BoolProperty(name = "Skip Validation", default = False,
        description = "Skipping validation might cause Blender to crash when the data is not valid",
        update = propertyChanged)

    def create(self):
        self.newInput("Vector List", "Vertex Locations", "vertexLocations", dataIsModified = True)
        self.newInput("Edge Indices List", "Edge Indices", "edgeIndices", dataIsModified = True)
        self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices", dataIsModified = True)
        self.newInput("Integer List", "Material Indices", "materialIndices", hide = True, dataIsModified = True)
        self.newOutput("an_MeshSocket", "Mesh", "meshData")

        materialIndicesSocket = self.inputs["Material Indices"]
        materialIndicesSocket.useIsUsedProperty = True
        materialIndicesSocket.isUsed = False

    def draw(self, layout):
        if self.skipValidation:
            layout.label(text = "Validation skipped", icon = "INFO")

    def drawAdvanced(self, layout):
        layout.prop(self, "skipValidation")

    def execute(self, vertexLocations, edgeIndices, polygonIndices, materialIndices):
        try:
            mesh = Mesh(vertexLocations, edgeIndices, polygonIndices, skipValidation = self.skipValidation)
            if self.inputs["Material Indices"].isUsed:
                if len(materialIndices) == len(polygonIndices) and materialIndices.getMinValue() >= 0:
                    mesh.insertBuiltInAttribute(Attribute("Material Indices", AttributeType.MATERIAL_INDEX,
                                                          AttributeDomain.FACE, AttributeDataType.INT,
                                                          materialIndices))
                else:
                    self.raiseErrorMessage("Invalid material indices.")
            return mesh

        except Exception as e:
            self.raiseErrorMessage(str(e))
