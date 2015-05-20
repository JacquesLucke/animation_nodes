import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *
from .. data_structures.curve import BezierSpline

class mn_BezierSplineSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_BezierSplineSocket"
    bl_label = "Bezier Spline Socket"
    dataType = "Bezier Spline"
    allowedInputTypes = ["Bezier Spline"]
    drawColor = (0.74, 0.36, 1.0, 1.0)
    
    objectName = bpy.props.StringProperty(default = "", description = "Use the first spline from this object", update = nodePropertyChanged)
    showName = bpy.props.BoolProperty(default = True)
    useWorldSpace = bpy.props.BoolProperty(default = True, description = "Convert points to world space")
    
    def drawInput(self, layout, node, text):
        row = layout.row(align = True)
        if self.showName:
            row.label(text)
        row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = "")
        props = row.operator("mn.assign_active_object_to_socket", text = "", icon = "EYEDROPPER")
        props.nodeTreeName = node.id_data.name
        props.nodeName = node.name
        props.isOutput = self.is_output
        props.socketName = self.name
        props.target = "objectName"
        row.prop(self, "useWorldSpace", text = "", icon = "WORLD")
        
    def getValue(self):
        try:
            object = bpy.data.objects.get(self.objectName)
            spline = BezierSpline.fromBlenderSpline(object.data.splines[0])
            if self.useWorldSpace: spline.transform(object.matrix_world)
            return spline
        except: return BezierSpline()
        
    def setStoreableValue(self, data):
        self.objectName  = data
    def getStoreableValue(self):
        return self.objectName

    def getCopyValueFunctionString(self):
        return "return value.copy()"