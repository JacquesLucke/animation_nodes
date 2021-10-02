import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Mesh, Attribute, AttributeType, AttributeDomain, AttributeDataType

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
        self.newInput("Boolean", "Load Custom Attributes", "loadCustomAttributes", value = False, hide = True)
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

        if meshRequired:
            yield "mesh = Mesh(vertexLocations, edgeIndices, polygonIndices, materialIndices)"
            yield "mesh.setVertexNormals(vertexNormals)"
            yield "mesh.setPolygonNormals(polygonNormals)"
            yield "mesh.setLoopEdges(sourceMesh.an.getLoopEdges())"
            yield "self.loadMaterialIndices('MATERIAL_INDEX', mesh, sourceMesh, evaluatedObject)"
            yield "if loadUVs: self.loadUVMaps('UV_MAP', mesh, sourceMesh, object)"
            yield "if loadVertexColors: self.loadVertexColors('VERTEX_COLOR', mesh, sourceMesh, object)"
            yield "if loadCustomAttributes: self.loadCustomAttributes('CUSTOM', mesh, sourceMesh, evaluatedObject)"

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

    def loadMaterialIndices(self, type, mesh, sourceMesh, object):
        if object.mode != "EDIT":
            mesh.insertBuiltInAttribute(Attribute("Material Indices",
                                                  AttributeType.MATERIAL_INDEX,
                                                  AttributeDomain.FACE,
                                                  AttributeDataType.INT,
                                                  sourceMesh.an.getPolygonMaterialIndices()))
        else:
            self.setErrorMessage("Object is in edit mode.")

    def loadUVMaps(self, type, mesh, sourceMesh, object):
        if object.mode != "EDIT":
            for uvMapName in sourceMesh.uv_layers.keys():
                mesh.insertUVMapAttribute(Attribute(uvMapName,
                                                    AttributeType.UV_MAP,
                                                    AttributeDomain.CORNER,
                                                    AttributeDataType.FLOAT2,
                                                    sourceMesh.an.getUVMap(uvMapName)))
        else:
            self.setErrorMessage("Object is in edit mode.")

    def loadVertexColors(self, type, mesh, sourceMesh, object):
        if object.mode != "EDIT":
            for colorLayerName in sourceMesh.vertex_colors.keys():
                mesh.insertVertexColorAttribute(Attribute(colorLayerName,
                                                          AttributeType.VERTEX_COLOR,
                                                          AttributeDomain.CORNER,
                                                          AttributeDataType.BYTE_COLOR,
                                                          sourceMesh.an.getVertexColorLayer(colorLayerName)))
        else:
            self.setErrorMessage("Object is in edit mode.")

    def loadCustomAttributes(self, type, mesh, sourceMesh, object):
        if object.mode != "EDIT":
            attributes = sourceMesh.attributes
            for customAttributeName in attributes.keys():
                attribute = attributes.get(customAttributeName)
                mesh.insertCustomAttribute(Attribute(customAttributeName,
                                                     AttributeType.CUSTOM,
                                                     AttributeDomain[attribute.domain],
                                                     AttributeDataType[attribute.data_type],
                                                     sourceMesh.an.getCustomAttribute(customAttributeName)))
        else:
            self.setErrorMessage("Object is in edit mode.")
