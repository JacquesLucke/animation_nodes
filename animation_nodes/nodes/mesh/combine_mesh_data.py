import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures import Mesh, LongList

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
        if not self.inputs["Material Indices"].isUsed:
            materialIndices = LongList(length = len(polygonIndices))
            materialIndices.fill(0)
        try:
            return Mesh(vertexLocations, edgeIndices, polygonIndices,
                    materialIndices, skipValidation = self.skipValidation)
        except Exception as e:
            self.raiseErrorMessage(str(e))
