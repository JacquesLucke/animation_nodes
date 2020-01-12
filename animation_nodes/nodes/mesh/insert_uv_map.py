import bpy
from ... data_structures import VirtualDoubleList, Vector2DList
from ... base_types import AnimationNode, VectorizedSocket

class InsertUVMapNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InsertUVMapNode"
    bl_label = "Insert UV Map"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
        self.newInput("Text", "Name", "uvMapName", value = "AN-UV Map")
        self.newInput("Float List", "X", "x")
        self.newInput("Float List", "Y", "y")

        self.newOutput("Mesh", "Mesh", "mesh")

    def execute(self, mesh, uvMapName, x, y):
        if uvMapName == "":
            self.raiseErrorMessage("UV map name can't be empty.")
        elif uvMapName in mesh.getVertexColorLayerNames():
            self.raiseErrorMessage(f"Mesh has already a uv map with the name '{uvMapName}'.")

        coLength = len(mesh.polygons.indices)
        xList = VirtualDoubleList.create(x, 0).materialize(coLength)
        yList = VirtualDoubleList.create(y, 0).materialize(coLength)

        coList = Vector2DList(length = coLength)
        for i in range(coLength):
            coList[i] = [xList[i], yList[i]]
        mesh.insertUVMap(uvMapName, coList)
        return mesh
