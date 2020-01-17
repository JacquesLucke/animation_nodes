import bpy
from ... data_structures import VirtualVector2DList
from ... base_types import AnimationNode, VectorizedSocket

class InsertUVMapNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InsertUVMapNode"
    bl_label = "Insert UV Map"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
        self.newInput("Text", "Name", "uvMapName", value = "AN-UV Map")
        self.newInput("Vector 2D List", "Vectors", "vectors")

        self.newOutput("Mesh", "Mesh", "mesh")

    def execute(self, mesh, uvMapName, vectors):
        if uvMapName == "":
            self.raiseErrorMessage("UV map name can't be empty.")
        elif uvMapName in mesh.getVertexColorLayerNames():
            self.raiseErrorMessage(f"Mesh has already a uv map with the name '{uvMapName}'.")

        vectors = VirtualVector2DList.create(vectors, [0, 0]).materialize(len(mesh.polygons.indices))
        mesh.insertUVMap(uvMapName, vectors)
        return mesh
