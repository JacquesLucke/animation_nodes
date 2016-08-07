import bpy
from bpy.props import *
from ... events import isRendering
from ... base_types.node import AnimationNode
from ... math.list_operations import transformVector3DList
from ... data_structures import Vector3DList, EdgeIndicesList

class ObjectMeshDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMeshDataNode"
    bl_label = "Object Mesh Data"

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Use World Space", "useWorldSpace", value = True)
        self.newInput("Boolean", "Use Modifiers", "useModifiers", value = False)
        self.newInput("Scene", "Scene", "scene", hide = True)

        self.newOutput("Vector List", "Vertex Locations", "vertexLocations")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")
        self.newOutput("String", "Mesh Name", "meshName", hide = True)

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        yield "meshName = ''"
        yield "if getattr(object, 'type', '') == 'MESH':"
        yield "    mesh = self.getMesh(object, useModifiers, scene)"
        yield "    meshName = mesh.name"

        if isLinked["vertexLocations"]:
            yield "    vertexLocations = self.getVertexLocations(mesh, object, useWorldSpace)"
        if isLinked["edgeIndices"]:
            yield "    edgeIndices = self.getEdgeIndices(mesh)"
        if isLinked["polygonIndices"]:
            yield "    polygonIndices = self.getPolygonIndices(mesh)"

        yield "    self.clearMesh(mesh, useModifiers, scene)"
        yield "else: vertexLocations, edgeIndices, polygonIndices = [], [], []"


    def getMesh(self, object, useModifiers, scene):
        if useModifiers and scene is not None:
            settings = "RENDER" if isRendering() else "PREVIEW"
            return object.to_mesh(scene = scene, apply_modifiers = True, settings = settings)
        return object.data

    def clearMesh(self, mesh, useModifiers, scene):
        if useModifiers and scene is not None: bpy.data.meshes.remove(mesh)


    def getVertexLocations(self, mesh, object, useWorldSpace):
        vertexLocations = Vector3DList(length = len(mesh.vertices))
        mesh.vertices.foreach_get("co", vertexLocations.getMemoryView())
        if useWorldSpace:
            transformVector3DList(vertexLocations, object.matrix_world)
        return vertexLocations

    def getEdgeIndices(self, mesh):
        edges = EdgeIndicesList(length = len(mesh.edges))
        mesh.edges.foreach_get("vertices", edges.getMemoryView())
        return edges

    def getPolygonIndices(self, mesh):
        return [tuple(face.vertices) for face in mesh.polygons]
