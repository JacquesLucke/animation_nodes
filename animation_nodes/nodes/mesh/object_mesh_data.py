import bpy
from bpy.props import *
from ... events import isRendering
from ... base_types import AnimationNode
from ... math.list_operations import transformVector3DList
from ... data_structures import (Vector3DList, EdgeIndicesList, PolygonIndicesList,
                                 FloatList, DoubleList)

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
        self.newOutput("Vector List", "Vertex Normals", "vertexNormals", hide = True)
        self.newOutput("Vector List", "Polygon Normals", "polygonNormals", hide = True)
        self.newOutput("Vector List", "Polygon Centers", "polygonCenters", hide = True)
        self.newOutput("Float List", "Local Polygon Areas", "localPolygonAreas", hide = True)
        self.newOutput("Text", "Mesh Name", "meshName", hide = True)

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
        if isLinked["vertexNormals"]:
            yield "    vertexNormals = self.getVertexNormals(mesh, object, useWorldSpace)"
        if isLinked["polygonNormals"]:
            yield "    polygonNormals = self.getPolygonNormals(mesh, object, useWorldSpace)"
        if isLinked["polygonCenters"]:
            yield "    polygonCenters = self.getPolygonCenters(mesh, object, useWorldSpace)"
        if isLinked["localPolygonAreas"]:
            yield "    localPolygonAreas = self.getLocalPolygonAreas(mesh)"

        yield "    self.clearMesh(mesh, useModifiers, scene)"
        yield "else:"
        yield "    vertexLocations = Vector3DList()"
        yield "    edgeIndices = EdgeIndicesList()"
        yield "    polygonIndices = PolygonIndicesList()"
        yield "    vertexNormals = Vector3DList()"
        yield "    polygonNormals = Vector3DList()"
        yield "    polygonCenters = Vector3DList()"
        yield "    localPolygonAreas = DoubleList()"


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
        polygons = PolygonIndicesList(
                        indicesAmount = len(mesh.loops),
                        polygonAmount = len(mesh.polygons))
        mesh.polygons.foreach_get("vertices", polygons.indices.getMemoryView())
        mesh.polygons.foreach_get("loop_total", polygons.polyLengths.getMemoryView())
        mesh.polygons.foreach_get("loop_start", polygons.polyStarts.getMemoryView())
        return polygons

    def getVertexNormals(self, mesh, object, useWorldSpace):
        normals = Vector3DList(length = len(mesh.vertices))
        mesh.vertices.foreach_get("normal", normals.getMemoryView())
        if useWorldSpace:
            transformVector3DList(normals, object.matrix_world, ignoreTranslation = True)
        return normals

    def getPolygonNormals(self, mesh, object, useWorldSpace):
        normals = Vector3DList(length = len(mesh.polygons))
        mesh.polygons.foreach_get("normal", normals.getMemoryView())
        if useWorldSpace:
            transformVector3DList(normals, object.matrix_world, ignoreTranslation = True)
        return normals

    def getPolygonCenters(self, mesh, object, useWorldSpace):
        centers = Vector3DList(length = len(mesh.polygons))
        mesh.polygons.foreach_get("center", centers.getMemoryView())
        if useWorldSpace:
            transformVector3DList(centers, object.matrix_world)
        return centers

    def getLocalPolygonAreas(self, mesh):
        areas = FloatList(length = len(mesh.polygons))
        mesh.polygons.foreach_get("area", areas.getMemoryView())
        return DoubleList.fromValues(areas)
