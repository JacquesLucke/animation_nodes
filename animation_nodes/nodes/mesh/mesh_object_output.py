import bpy
import bmesh
import numpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types import AnimationNode
from ... utils.animation import isAnimated
from ... data_structures import UShortList, AttributeType
from ... events import propertyChanged, executionCodeChanged

meshDataTypeItems = [
    ("MESH_DATA", "Mesh", "Mesh object that contains only vertex locations, edge indices and polygon indices", "", 0),
    ("BMESH", "BMesh", "BMesh object", "", 1),
    ("VERTICES", "Vertices", "A list of vertex locations; The length of this list has to be equal to the amount of vertices the mesh already has", "", 2) ]

class MeshObjectOutputNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_MeshObjectOutputNode"
    bl_label = "Mesh Object Output"
    bl_width_default = 180
    errorHandlingType = "MESSAGE"

    meshDataType: EnumProperty(name = "Mesh Type", default = "MESH_DATA",
        items = meshDataTypeItems, update = AnimationNode.refresh)

    validateMesh: BoolProperty(name = "Validate Mesh", default = False,
        description = "", update = propertyChanged)

    validateMeshVerbose: BoolProperty(name = "Validate Mesh Verbose", default = False,
        description = "Print results from validation in the console", update = propertyChanged)

    ensureAnimationData: BoolProperty(name = "Ensure Animation Data", default = True,
        description = ("Make sure that the mesh has animation data so that "
                       "it will be exported as animation by exporters (mainly Alembic)"),
        update = propertyChanged)

    calculateLooseEdges: BoolProperty(name = "Calculate Loose Edges", default = False,
        description = "Make sure Blender will draw edges that are not part of a polygon",
        update = propertyChanged)

    def create(self):
        socket = self.newInput("Object", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "MESH"

        if self.meshDataType == "MESH_DATA":
            self.newInput("Mesh", "Mesh", "meshData")
        elif self.meshDataType == "BMESH":
            self.newInput("BMesh", "BMesh", "bm")
        elif self.meshDataType == "VERTICES":
            self.newInput("Vector List", "Vertices", "vertices")

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False

        self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        if not self.meshInputSocket.hide:
            layout.prop(self, "meshDataType", text = "Type")

    @property
    def meshInputSocket(self):
        if self.meshDataType == "MESH_DATA": return self.inputs["Mesh"]
        if self.meshDataType == "BMESH": return self.inputs["BMesh"]
        if self.meshDataType == "VERTICES": return self.inputs["Vertices"]

    def drawAdvanced(self, layout):
        layout.prop(self, "ensureAnimationData")

        col = layout.column(align = True)
        col.prop(self, "validateMesh")
        subcol = col.column(align = True)
        subcol.active = self.validateMesh
        subcol.prop(self, "validateMeshVerbose", text = "Print Validation Info")

        layout.prop(self, "calculateLooseEdges")

    def getExecutionCode(self, required):
        if not self.isInputUsed(): return

        yield "if self.isValidObject(object):"
        yield "    mesh = object.data"

        if self.meshDataType == "MESH_DATA":
            yield "    self.setMesh(mesh, meshData, object)"
        elif self.meshDataType == "BMESH":
            yield "    self.setBMesh(mesh, bm)"
        elif self.meshDataType == "VERTICES":
            yield "    self.setVertices(mesh, vertices)"

        yield "    if self.ensureAnimationData:"
        yield "        self.ensureThatMeshHasAnimationData(mesh)"

    def isInputUsed(self):
        if self.meshDataType == "MESH_DATA":
            return self.inputs["Mesh"].isUsed
        elif self.meshDataType == "BMESH":
            return self.inputs["BMesh"].isUsed
        elif self.meshDataType == "VERTICES":
            return self.inputs["Vertices"].isUsed
        else:
            return False

    def isValidObject(self, object):
        if object is None: return False
        if object.type != "MESH":
            self.setErrorMessage("Object is not a mesh object.")
            return False
        if object.mode != "OBJECT":
            self.setErrorMessage("Object is not in object mode.")
            return False
        return True

    def setMesh(self, outMesh, mesh, object):
        # clear existing mesh
        bmesh.new().to_mesh(outMesh)

        # allocate memory
        outMesh.vertices.add(len(mesh.vertices))
        outMesh.edges.add(len(mesh.edges))
        outMesh.loops.add(len(mesh.polygons.indices))
        outMesh.polygons.add(len(mesh.polygons))

        # Vertices
        outMesh.vertices.foreach_set("co", mesh.vertices.asMemoryView())
        outMesh.vertices.foreach_set("normal", mesh.getVertexNormals().asMemoryView())

        # Edges
        outMesh.edges.foreach_set("vertices", mesh.edges.asMemoryView())

        # Polygons
        outMesh.polygons.foreach_set("loop_total", mesh.polygons.polyLengths.asMemoryView())
        outMesh.polygons.foreach_set("loop_start", mesh.polygons.polyStarts.asMemoryView())
        outMesh.loops.foreach_set("vertex_index", mesh.polygons.indices.asMemoryView())
        outMesh.loops.foreach_set("edge_index", mesh.getLoopEdges().asMemoryView())

        # Materials Indices
        materialIndices = mesh.getBuiltInAttribute("Material Indices")
        if materialIndices is not None:
            indices = materialIndices.data
            if len(indices) > 0 and indices.getMaxValue() > 0 and indices.getMinValue() >= 0:
                indices = UShortList.fromValues(indices)
                outMesh.polygons.foreach_set("material_index", indices.asMemoryView())

        # UV Maps
        for attribute in mesh.iterUVMapAttributes():
            uvLayer = outMesh.uv_layers.new(name = attribute.name, do_init = False)
            uvLayer.data.foreach_set("uv", attribute.data.asMemoryView())

        # Vertex Color Layers
        for attribute in mesh.iterVertexColorAttributes():
            vertexColorLayer = outMesh.vertex_colors.new(name = attribute.name, do_init = False)
            vertexColorLayer.data.foreach_set("color", attribute.data.asMemoryView())

        # Vertex Groups
        vertexAmount = len(outMesh.vertices)
        for attribute in mesh.iterVertexWeightAttributes():
            vertexGroup = object.vertex_groups.get(attribute.name)
            if vertexGroup is None:
                vertexGroup = object.vertex_groups.new(name = attribute.name)
            weights = attribute.data
            for i in range(vertexAmount):
                vertexGroup.add([i], weights[i], "REPLACE")
        object.data.update()

        # Custom Attributes
        for attribute in mesh.iterCustomAttributes():
            domain = attribute.getDomainAsString()
            dataType = attribute.getListTypeAsString()
            data = attribute.data

            attributeOut = outMesh.attributes.new(attribute.name, dataType, domain)

            if dataType in ("FLOAT", "INT", "INT32_2D"):
                attributeOut.data.foreach_set("value", data.asMemoryView())
            elif dataType in ("FLOAT2", "FLOAT_VECTOR"):
                attributeOut.data.foreach_set("vector", data.asMemoryView())
            elif dataType == "BOOLEAN":
                attributeOut.data.foreach_set("value", numpy.not_equal(data.asNumpyArray(), b'\0'))
            else:
                attributeOut.data.foreach_set("color", data.asMemoryView())

        if self.validateMesh:
            outMesh.validate(verbose = self.validateMeshVerbose)

        if self.calculateLooseEdges:
            outMesh.update(calc_edges_loose = True)

    def setBMesh(self, mesh, bm):
        bm.to_mesh(mesh)

    def setVertices(self, mesh, vertices):
        if len(mesh.vertices) != len(vertices):
            self.setErrorMessage("The vertex amounts are not equal.")
            return object

        mesh.vertices.foreach_set("co", vertices.asMemoryView())
        mesh.update()

    def ensureThatMeshHasAnimationData(self, mesh):
        if not isAnimated(mesh):
            mesh['an_helper_property'] = 0
            mesh.keyframe_insert(data_path = '["an_helper_property"]')
