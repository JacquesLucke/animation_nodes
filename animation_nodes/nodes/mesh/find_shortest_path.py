import bpy
from bpy.props import *
from ... data_structures import Mesh, LongList, Vector3DList
from ... base_types import AnimationNode, VectorizedSocket
from ... algorithms.mesh_generation.find_shortest_path import getShortestPath

modeItems = [
    ("INDEX", "Index", "Path from source vertex to other vertex", 0),
    ("ALL", "All", "Paths from source vertex to other vertices", 1)
]

pathTypeItems = [
    ("MESH", "Mesh", "Paths as line mesh(es)", 0),
    ("SPLINE", "Spline", "Paths as poly splines", 1),
    ("STROKE", "Stroke", "Paths as gp strokes", 2)
]

class FindShortestPathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindShortestPathNode"
    bl_label = "Find Shortest Path"
    errorHandlingType = "EXCEPTION"

    mode: EnumProperty(name = "Mode Type", default = "ALL",
        items = modeItems, update = AnimationNode.refresh)

    pathType: EnumProperty(name = "Path Type", default = "MESH",
        items = pathTypeItems, update = AnimationNode.refresh)

    joinMeshes: BoolProperty(name = "Join Meshes", default = True,
        update = AnimationNode.refresh)

    useSourceList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        if self.mode == "INDEX":
            self.newInput("Integer", "Source", "source")
            self.newInput("Integer", "Destiny", "destiny", value = 1)
        else:
            self.newInput(VectorizedSocket("Integer", "useSourceList",
                    ("Source", "sources"), ("Sources", "sources")))
        self.newInput("Boolean", "Change Direction", "changeDirection", value = False)

        if self.pathType == "MESH":
            if not self.joinMeshes:
                self.newOutput("Mesh List", "Meshes", "outMeshes")
            else:
                self.newOutput("Mesh", "Mesh", "outMesh")
        elif self.pathType == "SPLINE":
            self.newOutput("Spline List", "Splines", "outSplines")
        elif self.pathType == "STROKE":
            self.newOutput("GPStroke List", "Strokes", "outStrokes")
        if self.mode == "INDEX":
            self.newOutput("Vector List", "Vectors", "vectors")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")
        layout.prop(self, "pathType", text = "")
        if self.pathType == "MESH":
            layout.prop(self, "joinMeshes")

    def getExecutionFunctionName(self):
        if self.mode == "INDEX":
            return "execute_Index"
        else:
            return "execute_All"

    def execute_Index(self, mesh, source, destiny, changeDirection):
        if mesh is None:
            if self.joinMeshes and self.pathType == "MESH":
                return Mesh(), Vector3DList()
            else:
                return [], Vector3DList()

        if source < 0 or source >= len(mesh.vertices):
            self.raiseErrorMessage("Some indices are out of range.")
        if destiny < 0 or destiny >= len(mesh.vertices):
            self.raiseErrorMessage("Some indices are out of range.")

        sources = LongList.fromValue(source)
        destinies = LongList.fromValue(destiny)
        if self.pathType == "MESH":
            if self.joinMeshes:
                return Mesh.join(*getShortestPath(mesh, sources, destinies, "MESH", "INDEX", changeDirection))
            else:
                return getShortestPath(mesh, sources, destinies, "MESH", "INDEX", changeDirection)
        elif self.pathType == "SPLINE":
            return getShortestPath(mesh, sources, destinies, "SPLINE", "INDEX", changeDirection)
        elif self.pathType == "STROKE":
            return getShortestPath(mesh, sources, destinies, "STROKE", "INDEX", changeDirection)

    def execute_All(self, mesh, sources, changeDirection):
        if not self.useSourceList: sources = LongList.fromValue(sources)
        if mesh is None or len(sources) == 0:
            if self.joinMeshes and self.pathType == "MESH":
                return Mesh()
            else:
                return []

        if sources.getMinValue() < 0 or sources.getMaxValue() >= len(mesh.vertices):
            self.raiseErrorMessage("Some indices are out of range.")

        if self.pathType == "MESH":
            if self.joinMeshes:
                return Mesh.join(*getShortestPath(mesh, sources, LongList(), "MESH", "ALL", changeDirection))
            else:
                return getShortestPath(mesh, sources, LongList(), "MESH", "ALL", changeDirection)
        elif self.pathType == "SPLINE":
            return getShortestPath(mesh, sources, LongList(), "SPLINE", "ALL", changeDirection)
        elif self.pathType == "STROKE":
            return getShortestPath(mesh, sources, LongList(), "STROKE", "ALL", changeDirection)
