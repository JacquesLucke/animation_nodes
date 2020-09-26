import bpy
from bpy.props import *
from mathutils.bvhtree import BVHTree
from .. events import propertyChanged
from .. utils.depsgraph import getEvaluatedID
from .. base_types import AnimationNodeSocket

class BVHTreeSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_BVHTreeSocket"
    bl_label = "BVHTree Socket"
    dataType = "BVHTree"
    drawColor = (0.18, 0.32, 0.32, 1)
    comparable = True
    storable = True

    object: PointerProperty(type = bpy.types.Object,
        description = "Construct a tree from this object",
        update = propertyChanged)

    useWorldSpace: BoolProperty(default = True,
        description = "Convert mesh to world space",
        update = propertyChanged)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop(self, "object", text = text)
        self.invokeFunction(row, node, "handleEyedropperButton", icon = "EYEDROPPER", passEvent = True,
            description = "Assign active object to this socket (hold CTRL to open a rename object dialog)")
        if self.object:
            row.prop(self, "useWorldSpace", text = "", icon = "WORLD")

    def getValue(self):
        if getattr(self.object, "type", "") != "MESH":
            return self.getDefaultValue()

        evaluatedObject = getEvaluatedID(self.object)
        mesh = evaluatedObject.data
        polygons = mesh.an.getPolygonIndices()
        if len(polygons) == 0:
            return self.getDefaultValue()
        vertices = mesh.an.getVertices()
        if self.useWorldSpace:
            vertices.transform(evaluatedObject.matrix_world)
        return BVHTree.FromPolygons(vertices, polygons)

    def setProperty(self, data):
        self.object, self.useWorldSpace = data

    def getProperty(self):
        return self.object, self.useWorldSpace

    def handleEyedropperButton(self, event):
        if event.ctrl:
            bpy.ops.an.rename_datablock_popup("INVOKE_DEFAULT",
                oldName = self.object.name,
                path = "bpy.data.objects",
                icon = "OUTLINER_OB_MESH")
        else:
            object = bpy.context.active_object
            if getattr(object, "type", "") == "MESH":
                self.object = object

    @classmethod
    def getDefaultValue(cls):
        return BVHTree.FromPolygons(vertices = [], polygons = [])

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, BVHTree):
            return value, 0
        return cls.getDefaultValue(), 2
