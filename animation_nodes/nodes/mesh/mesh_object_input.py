import bpy
from bpy.props import *
from ... data_structures import Mesh, BooleanList
from ... base_types import AnimationNode, VectorizedSocket

class MeshObjectInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshObjectInputNode"
    bl_label = "Mesh Object Input"
    errorHandlingType = "MESSAGE"
    searchTags = ["Object Mesh Data", "Mesh from Object"]

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Use World Space", "useWorldSpace")
        self.newInput("Boolean", "Use Modifiers", "useModifiers", value = False)
        self.newInput("Boolean", "Load UVs", "loadUVs", value = False, hide = True)
        self.newInput("Boolean", "Load Vertex Colors", "loadVertexColors", value = False, hide = True)
        self.newInput("Scene", "Scene", "scene", hide = True)

        self.newOutput("Mesh", "Mesh", "mesh")

        self.newOutput("Vector List", "Vertex Locations", "vertexLocations")
        self.newOutput("Vector List", "Vertex Normals", "vertexNormals")

        self.newOutput("Vector List", "Polygon Centers", "polygonCenters")
        self.newOutput("Vector List", "Polygon Normals", "polygonNormals")

        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

        self.newOutput("Float List", "Local Polygon Areas", "localPolygonAreas")
        self.newOutput("Integer List", "Material Indices", "materialIndices")

        self.newOutput("Boolean List", "Vertices Selection Mask", "verticesSelectionMask")
        self.newOutput("Boolean List", "Edges Selection Mask", "edgesSelectionMask")
        self.newOutput("Boolean List", "Polygons Selection Mask", "polygonsSelectionMask")

        self.newOutput("Text", "Mesh Name", "meshName")

        visibleOutputs = ("Mesh", "Vertex Locations", "Polygon Centers")
        for socket in self.outputs:
            socket.hide = socket.name not in visibleOutputs

    def draw(self, layout):
        pass

    def getExecutionCode(self, required):
        if len(required) == 0:
            return

        yield "sourceMesh = object.an.getMesh(useModifiers) if object else None"
        yield "if sourceMesh is not None:"
        yield from ("    " + line for line in self.iterGetMeshDataCodeLines(required))
        yield "    if sourceMesh.users == 0: object.to_mesh_clear()"
        yield "else:"
        yield "    meshName = ''"
        yield "    mesh = Mesh()"
        yield "    vertexLocations = Vector3DList()"
        yield "    edgeIndices = EdgeIndicesList()"
        yield "    polygonIndices = PolygonIndicesList()"
        yield "    vertexNormals = Vector3DList()"
        yield "    polygonNormals = Vector3DList()"
        yield "    polygonCenters = Vector3DList()"
        yield "    localPolygonAreas = DoubleList()"
        yield "    materialIndices = LongList()"
        yield "    verticesSelectionMask = BooleanList()"
        yield "    edgesSelectionMask = BooleanList()"
        yield "    polygonsSelectionMask = BooleanList()"

    def iterGetMeshDataCodeLines(self, required):
        if "meshName" in required:
            yield "meshName = sourceMesh.name"

        yield "evaluatedObject = AN.utils.depsgraph.getEvaluatedID(object)"
        meshRequired = "mesh" in required

        if "vertexLocations" in required or meshRequired:
            yield "vertexLocations = self.getVertexLocations(sourceMesh, evaluatedObject, useWorldSpace)"
        if "edgeIndices" in required or meshRequired:
            yield "edgeIndices = sourceMesh.an.getEdgeIndices()"
        if "polygonIndices" in required or meshRequired:
            yield "polygonIndices = sourceMesh.an.getPolygonIndices()"
        if "vertexNormals" in required or meshRequired:
            yield "vertexNormals = self.getVertexNormals(sourceMesh, evaluatedObject, useWorldSpace)"
        if "polygonNormals" in required or meshRequired:
            yield "polygonNormals = self.getPolygonNormals(sourceMesh, evaluatedObject, useWorldSpace)"
        if "polygonCenters" in required:
            yield "polygonCenters = self.getPolygonCenters(sourceMesh, evaluatedObject, useWorldSpace)"
        if "localPolygonAreas" in required:
            yield "localPolygonAreas = DoubleList.fromValues(sourceMesh.an.getPolygonAreas())"
        if "materialIndices" in required or meshRequired:
            yield "materialIndices = LongList.fromValues(sourceMesh.an.getPolygonMaterialIndices())"
        if "verticesSelectionMask" in required:
            yield "verticesSelectionMask = self.getVerticesSelectionMask(evaluatedObject)"
        if "edgesSelectionMask" in required:
            yield "edgesSelectionMask = self.getEdgesSelectionMask(evaluatedObject)"
        if "polygonsSelectionMask" in required:
            yield "polygonsSelectionMask = self.getPolygonsSelectionMask(evaluatedObject)"

        if meshRequired:
            yield "mesh = Mesh(vertexLocations, edgeIndices, polygonIndices, materialIndices)"
            yield "mesh.setVertexNormals(vertexNormals)"
            yield "mesh.setPolygonNormals(polygonNormals)"
            yield "mesh.setLoopEdges(sourceMesh.an.getLoopEdges())"
            yield "if loadUVs: self.loadUVs(mesh, sourceMesh, object)"
            yield "if loadVertexColors: self.loadVertexColors(mesh, sourceMesh, object)"

    def getVertexLocations(self, mesh, object, useWorldSpace):
        vertices = mesh.an.getVertices()
        if useWorldSpace:
            vertices.transform(object.matrix_world)
        return vertices

    def getVertexNormals(self, mesh, object, useWorldSpace):
        normals = mesh.an.getVertexNormals()
        if useWorldSpace:
            normals.transform(object.matrix_world, ignoreTranslation = True)
        return normals

    def getPolygonNormals(self, mesh, object, useWorldSpace):
        normals = mesh.an.getPolygonNormals()
        if useWorldSpace:
            normals.transform(object.matrix_world, ignoreTranslation = True)
        return normals

    def getPolygonCenters(self, mesh, object, useWorldSpace):
        centers = mesh.an.getPolygonCenters()
        if useWorldSpace:
            centers.transform(object.matrix_world)
        return centers

    def getVerticesSelectionMask(self, object):
        vertices = object.data.vertices
        mask = [False] * len(vertices)
        vertices.foreach_get("select", mask)
        return BooleanList.fromValues(mask)

    def getEdgesSelectionMask(self, object):
        edges = object.data.edges
        mask = [False] * len(edges)
        edges.foreach_get("select", mask)
        return BooleanList.fromValues(mask)

    def getPolygonsSelectionMask(self, object):
        polygons = object.data.polygons
        mask = [False] * len(polygons)
        polygons.foreach_get("select", mask)
        return BooleanList.fromValues(mask)

    def loadUVs(self, mesh, sourceMesh, object):
        if object.mode == "OBJECT":
            for uvMapName in sourceMesh.uv_layers.keys():
                mesh.insertUVMap(uvMapName, sourceMesh.an.getUVMap(uvMapName))
        else:
            self.setErrorMessage("Object has to be in object mode to load UV maps.")

    def loadVertexColors(self, mesh, sourceMesh, object):
        if object.mode != "EDIT":
            for colorLayerName in sourceMesh.vertex_colors.keys():
                mesh.insertVertexColorLayer(colorLayerName, sourceMesh.an.getVertexColorLayer(colorLayerName))
        else:
            self.setErrorMessage("Object is in edit mode.")
