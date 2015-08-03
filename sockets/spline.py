import bpy
from bpy.props import *
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. data_structures.splines.from_blender import createSplinesFromBlenderObject
from .. data_structures.splines.bezier_spline import BezierSpline

class mn_SplineSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_SplineSocket"
    bl_label = "Spline Socket"
    dataType = "Spline"
    allowedInputTypes = ["Spline"]
    drawColor = (0.74, 0.36, 1.0, 1.0)

    objectName = StringProperty(default = "", description = "Use the first spline from this object", update = nodePropertyChanged)
    showName = BoolProperty(default = True)
    useWorldSpace = BoolProperty(default = True, description = "Convert points to world space", update = nodePropertyChanged)
    showObjectInput = BoolProperty(default = True)

    def drawInput(self, layout, node, text):
        row = layout.row(align = True)

        if self.showName: row.label(text)

        if self.showObjectInput:
            row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = "")
            props = row.operator("mn.assign_active_object_to_socket", text = "", icon = "EYEDROPPER")
            props.nodeTreeName = node.id_data.name
            props.nodeName = node.name
            props.isOutput = self.is_output
            props.socketName = self.name
            props.target = "objectName"
            if self.objectName != "":
                row.prop(self, "useWorldSpace", text = "", icon = "WORLD")

    def getValue(self):
        object = bpy.data.objects.get(self.objectName)
        splines = createSplinesFromBlenderObject(object)
        if self.useWorldSpace:
            for spline in splines:
                spline.transform(object.matrix_world)
        if len(splines) > 0: return splines[0]
        else: return BezierSpline()

    def setStoreableValue(self, data):
        self.objectName, self.useWorldSpace = data
    def getStoreableValue(self):
        return (self.objectName, self.useWorldSpace)

    def getCopyValueFunctionString(self):
        return "return value.copy()"
