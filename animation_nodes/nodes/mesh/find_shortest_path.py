import bpy
from bpy.props import *
from ... data_structures import Mesh, LongList, Vector3DList
from ... base_types import AnimationNode, VectorizedSocket
from ... algorithms.mesh_generation.find_shortest_path import getShortestPath

modeItems = [
    ("PATH", "Path", "Find path from source vertex to other vertex", 0),
    ("TREE", "Tree", "Find paths from source vertex(ies) to other vertices", 1)
]

pathTypeItems = [
    ("MESH", "Mesh", "Output paths as line mesh(es)", 0),
    ("SPLINE", "Spline", "Output paths as poly splines", 1),
    ("STROKE", "Stroke", "Output paths as gp strokes", 2)
]

class FindShortestPathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindShortestPathNode"
    bl_label = "Find Shortest Path"
    errorHandlingType = "EXCEPTION"

    mode: EnumProperty(name = "Mode Type", default = "TREE",
        items = modeItems, update = AnimationNode.refresh)

    pathType: EnumProperty(name = "Path Type", default = "MESH",
        items = pathTypeItems, update = AnimationNode.refresh)

    joinMeshes: BoolProperty(name = "Join Meshes", default = True,
        update = AnimationNode.refresh)

    useSourceList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        if self.mode == "PATH":
            self.newInput("Integer", "Source", "source")
            self.newInput("Integer", "Target", "target", value = 1)
        else:
            self.newInput(VectorizedSocket("Integer", "useSourceList",
                    ("Source", "sources"), ("Sources", "sources")))

        if self.mode == "PATH":
            self.newOutput("Integer List", "Indices", "indices")
        else:
            if self.pathType == "MESH":
                if not self.joinMeshes:
                    self.newOutput("Mesh List", "Meshes", "outMeshes")
                else:
                    self.newOutput("Mesh", "Mesh", "outMesh")
            elif self.pathType == "SPLINE":
                self.newOutput("Spline List", "Splines", "outSplines")
            elif self.pathType == "STROKE":
                self.newOutput("GPStroke List", "Strokes", "outStrokes")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")
        layout.prop(self, "pathType", text = "")
        if self.pathType == "MESH":
            layout.prop(self, "joinMeshes")

    def getExecutionFunctionName(self):
        if self.mode == "PATH":
            return "execute_Index"
        else:
            return "execute_All"

    def execute_Index(self, mesh, source, target):
        if mesh is None:
            return LongList()

        if source < 0 or source >= len(mesh.vertices):
            self.raiseErrorMessage("Some indices are out of range.")
        if target < 0 or target >= len(mesh.vertices):
            self.raiseErrorMessage("Some indices are out of range.")

        sources = LongList.fromValue(source)
        targets = LongList.fromValue(target)
        if self.pathType == "MESH":
            if self.joinMeshes:
                return Mesh.join(*getShortestPath(mesh, sources, targets, "MESH", "PATH"))
            else:
                return getShortestPath(mesh, sources, targets, "MESH", "PATH")
        elif self.pathType == "SPLINE":
            return getShortestPath(mesh, sources, targets, "SPLINE", "PATH")
        elif self.pathType == "STROKE":
            return getShortestPath(mesh, sources, targets, "STROKE", "PATH")

    def execute_All(self, mesh, sources):
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
                return Mesh.join(*getShortestPath(mesh, sources, LongList(), "MESH", "TREE"))
            else:
                return getShortestPath(mesh, sources, LongList(), "MESH", "TREE")
        elif self.pathType == "SPLINE":
            return getShortestPath(mesh, sources, LongList(), "SPLINE", "TREE")
        elif self.pathType == "STROKE":
            return getShortestPath(mesh, sources, LongList(), "STROKE", "TREE")
