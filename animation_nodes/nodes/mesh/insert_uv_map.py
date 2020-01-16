import bpy
from ... base_types import AnimationNode, VectorizedSocket

class InsertUVMapNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InsertUVMapNode"
    bl_label = "Insert UV Map"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
        self.newInput("Text", "Name", "uvMapName", value = "AN-UV Map")
        self.newInput("Vector 2D List", "Vectors2D", "vectors2D")

        self.newOutput("Mesh", "Mesh", "mesh")

    def execute(self, mesh, uvMapName, vectors2D):
        if uvMapName == "":
            self.raiseErrorMessage("UV map name can't be empty.")
        elif uvMapName in mesh.getVertexColorLayerNames():
            self.raiseErrorMessage(f"Mesh has already a uv map with the name '{uvMapName}'.")

        coLength = len(mesh.polygons.indices)
        if len(vectors2D) != coLength:
            self.raiseErrorMessage("Invaild input vectors 2D list.")

        mesh.insertUVMap(uvMapName, vectors2D)
        return mesh
