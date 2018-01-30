import bpy
from bpy.props import *
from ... data_structures import Mesh
from ... events import propertyChanged
from ... base_types import AnimationNode

sourceItems = [
    ("MESH_DATA", "Mesh Data", "", "OUTLINER_DATA_MESH", 0),
    ("OBJECT", "Object", "", "OBJECT_DATAMODE", 1)
]

class ConstructMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConstructMeshNode"
    bl_label = "Construct Mesh"
    errorHandlingType = "EXCEPTION"

    source = EnumProperty(name = "Source", default = "OBJECT",
        items = sourceItems, update = AnimationNode.refresh)

    useUVs = BoolProperty(name = "Use UVs", default = False,
        update = propertyChanged)

    def create(self):
        if self.source == "MESH_DATA":
            self.newInput("Vector List", "Vertices", "vertices")
            self.newInput("Edge Indices List", "Edge Indices", "edgeIndices")
            self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices")
        elif self.source == "OBJECT":
            self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
            self.newInput("Boolean", "Use World Space", "useWorldSpace", value = False)
            self.newInput("Boolean", "Use Modifiers", "useModifiers", value = False)
            self.newInput("Scene", "Scene", "scene", hide = True)
        self.newOutput("Mesh", "Mesh", "mesh")

    def draw(self, layout):
        layout.prop(self, "source", text = "")
        layout.prop(self, "useUVs", toggle = True)

    def getExecutionFunctionName(self):
        if self.source == "MESH_DATA":
            return "execute_MeshData"
        elif self.source == "OBJECT":
            return "execute_Object"

    def execute_MeshData(self, vertices, edgeIndices, polygonIndices):
        try:
            return Mesh(vertices, edgeIndices, polygonIndices)
        except Exception as e:
            self.raiseErrorMessage(str(e))

    def execute_Object(self, object, useWorldSpace, useModifiers, scene):
        if object is None:
            return Mesh()

        sourceMesh = object.an.getMesh(scene, useModifiers)
        if sourceMesh is None:
            return Mesh()

        vertices = sourceMesh.an.getVertices()
        if useWorldSpace:
            vertices.transform(object.matrix_world)

        edges = sourceMesh.an.getEdgeIndices()
        polygons = sourceMesh.an.getPolygonIndices()

        outMesh = Mesh(vertices, edges, polygons, skipValidation = True)

        if self.useUVs:
            if object.mode == "OBJECT":
                for uvMapName in sourceMesh.uv_layers.keys():
                    outMesh.insertUVMap(uvMapName, sourceMesh.an.getUVMap(uvMapName))


        if sourceMesh.users == 0:
            bpy.data.meshes.remove(sourceMesh)

        return outMesh
