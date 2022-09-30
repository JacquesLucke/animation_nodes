import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

quadMethodItems = [
    ("BEAUTY", "Beauty", "NONE", 0),
    ("FIXED", "Fixed", "NONE", 1),
    ("ALTERNATE", "Alternate", "NONE", 2),
    ("SHORT_EDGE", "Short Edge", "NONE", 3)
]

ngonMethodItems = [
    ("BEAUTY", "Beauty", "NONE", 0),
    ("EAR_CLIP", "Ear Clip", "NONE", 1),
]

class BMeshTriangulateNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_BMeshTriangulateNode"
    bl_label = "Triangulate BMesh"
    bl_width_default = 160

    quad: EnumProperty(name = "Quad Method", default = "BEAUTY",
          description = "Select a quad triangulation method",
          items = quadMethodItems, update = propertyChanged)

    ngon: EnumProperty(name = "Ngon Method", default = "BEAUTY",
          description = "Select a ngon triangulation method",
          items = ngonMethodItems, update = propertyChanged)

    def create(self):
        self.newInput("BMesh", "BMesh", "bm", dataIsModified = True)
        self.newOutput("BMesh", "BMesh", "bm")
        self.newOutput("Integer List", "Source Ngon Indices", "ngonIndices", hide = True)

    def drawAdvanced(self, layout):
        layout.prop(self, "quad")
        layout.prop(self, "ngon")

    def getExecutionCode(self, required):

        yield "faces = bm.faces"

        # do not invert isLinked order, this needs original faces
        if "ngonIndices" in required:
            yield "ngonIndices = list(range(len(faces)))"
            yield "for face in faces:"
            yield "    indf = face.index"
            yield "    lenf = len(face.verts) - 3"
            yield "    if lenf > 0: ngonIndices.extend(indf for i in range(lenf))"

        if "bm" in required:
            yield "bmesh.ops.triangulate(bm, faces = faces,"
            yield "    quad_method = self.quad, ngon_method = self.ngon)"

    def getUsedModules(self):
        return ["bmesh"]
