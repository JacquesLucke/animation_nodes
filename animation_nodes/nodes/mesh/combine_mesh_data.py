import bpy
from ... data_structures import Mesh
from ... base_types import AnimationNode

class CombineMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineMeshNode"
    bl_label = "Combine Mesh"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Vector List", "Vertex Locations", "vertexLocations", dataIsModified = True)
        self.newInput("Edge Indices List", "Edge Indices", "edgeIndices", dataIsModified = True)
        self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices", dataIsModified = True)
        self.newOutput("an_MeshSocket", "Mesh", "meshData")

    def execute(self, vertexLocations, edgeIndices, polygonIndices):
        try: return Mesh(vertexLocations, edgeIndices, polygonIndices)
        except Exception as e:
            self.raiseErrorMessage(str(e))
