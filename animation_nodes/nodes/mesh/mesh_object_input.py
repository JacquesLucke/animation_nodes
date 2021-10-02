import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Mesh, Attribute, AttributeType, AttributeDomain, AttributeDataType, DoubleList

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
        self.newInput("Boolean", "Load Vertex Weights", "loadVertexWeights", value = False, hide = True)
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
        self.newOutput("Float List", "Bevel Vertex Weights", "bevelVertexWeights")
        self.newOutput("Float List", "Bevel Edge Weights", "bevelEdgeWeights")
        self.newOutput("Float List", "Edge Creases", "edgeCreases")

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
        yield "    bevelVertexWeights = DoubleList()"
        yield "    bevelEdgeWeights = DoubleList()"
        yield "    edgeCreases = DoubleList()"

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
        if "bevelVertexWeights" in required or meshRequired:
            yield "bevelVertexWeights = DoubleList.fromValues(sourceMesh.an.getBevelVertexWeights())"
        if "bevelEdgeWeights" in required or meshRequired:
            yield "bevelEdgeWeights = DoubleList.fromValues(sourceMesh.an.getBevelEdgeWeights())"
        if "edgeCreases" in required or meshRequired:
            yield "edgeCreases = DoubleList.fromValues(sourceMesh.an.getEdgeCreases())"

        if meshRequired:
            yield "mesh = Mesh(vertexLocations, edgeIndices, polygonIndices)"
            yield "mesh.setVertexNormals(vertexNormals)"
            yield "mesh.setPolygonNormals(polygonNormals)"
            yield "mesh.setLoopEdges(sourceMesh.an.getLoopEdges())"
            yield "self.loadBuiltInAttributes(mesh, sourceMesh, evaluatedObject)"
            yield "if loadUVs: self.loadUVMaps(mesh, sourceMesh, object)"
            yield "if loadVertexColors: self.loadVertexColors(mesh, sourceMesh, object)"
            yield "if loadVertexWeights: self.loadVertexWeights(mesh, sourceMesh, object, useModifiers, scene)"
            yield "if loadCustomAttributes: self.loadCustomAttributes(mesh, sourceMesh, evaluatedObject)"

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

    def loadBuiltInAttributes(self, mesh, sourceMesh, object):
        if object.mode != "EDIT":
            mesh.insertBuiltInAttribute(Attribute("Material Indices",
                                                  AttributeType.MATERIAL_INDEX,
                                                  AttributeDomain.FACE,
                                                  AttributeDataType.INT,
                                                  sourceMesh.an.getPolygonMaterialIndices()))

            mesh.insertBuiltInAttribute(Attribute("Bevel Edge Weights",
                                                  AttributeType.BEVEL_EDGE_WEIGHT,
                                                  AttributeDomain.EDGE,
                                                  AttributeDataType.FLOAT,
                                                  sourceMesh.an.getBevelEdgeWeights()))

            mesh.insertBuiltInAttribute(Attribute("Bevel Vertex Weights",
                                                  AttributeType.BEVEL_VERTEX_WEIGHT,
                                                  AttributeDomain.POINT,
                                                  AttributeDataType.FLOAT,
                                                  sourceMesh.an.getBevelVertexWeights()))

            mesh.insertBuiltInAttribute(Attribute("Edge Creases",
                                                  AttributeType.EDGE_CREASE,
                                                  AttributeDomain.EDGE,
                                                  AttributeDataType.FLOAT,
                                                  sourceMesh.an.getEdgeCreases()))

        else:
            self.setErrorMessage("Object is in edit mode.")

    def loadUVMaps(self, mesh, sourceMesh, object):
        if object.mode != "EDIT":
            for uvMapName in sourceMesh.uv_layers.keys():
                mesh.insertUVMapAttribute(Attribute(uvMapName,
                                                    AttributeType.UV_MAP,
                                                    AttributeDomain.CORNER,
                                                    AttributeDataType.FLOAT2,
                                                    sourceMesh.an.getUVMap(uvMapName)))
        else:
            self.setErrorMessage("Object is in edit mode.")

    def loadVertexColors(self, mesh, sourceMesh, object):
        if object.mode != "EDIT":
            for colorLayerName in sourceMesh.vertex_colors.keys():
                mesh.insertVertexColorAttribute(Attribute(colorLayerName,
                                                          AttributeType.VERTEX_COLOR,
                                                          AttributeDomain.CORNER,
                                                          AttributeDataType.BYTE_COLOR,
                                                          sourceMesh.an.getVertexColorLayer(colorLayerName)))
        else:
            self.setErrorMessage("Object is in edit mode.")

    def loadVertexWeights(self, mesh, sourceMesh, object, useModifiers, scene):
        if object.mode != "EDIT":
            vertexGroups = object.vertex_groups
            for vertexGroupName in vertexGroups.keys():
                if useModifiers:
                    weights = DoubleList(length = len(mesh.vertices))
                    weights.fill(0)
                else:
                    weights = self.execute_All_WithoutModifiers(mesh, vertexGroups[vertexGroupName])
                mesh.insertVertexWeightAttribute(Attribute(vertexGroupName,
                                                           AttributeType.VERTEX_WEIGHT,
                                                           AttributeDomain.POINT,
                                                           AttributeDataType.FLOAT,
                                                           weights))
        else:
            self.setErrorMessage("Object is in edit mode.")

    def loadCustomAttributes(self, mesh, sourceMesh, object):
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

    def execute_All_WithoutModifiers(self, mesh, vertexGroup):
        vertexAmount = len(mesh.vertices)
        weights = DoubleList(length = vertexAmount)
        getWeight = vertexGroup.weight

        for i in range(vertexAmount):
            try: weights[i] = getWeight(i)
            except: weights[i] = 0
        return weights
