import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *
from .. data_structures.curve import BezierCurve

class mn_BezierCurveSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_BezierCurveSocket"
    bl_label = "Bezier Curve Socket"
    dataType = "Bezier Curve"
    allowedInputTypes = ["Bezier Curve"]
    drawColor = (0.38, 0.03, 1.0, 1.0)
    
    objectName = bpy.props.StringProperty(default = "", description = "Use the curve from this object", update = nodePropertyChanged)
    
    def drawInput(self, layout, node, text):
        row = layout.row(align = True)
        row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = "")
        props = row.operator("mn.assign_active_object_to_socket", text = "", icon = "EYEDROPPER")
        props.nodeTreeName = node.id_data.name
        props.nodeName = node.name
        props.isOutput = self.is_output
        props.socketName = self.name
        props.target = "objectName"
        
    def getValue(self):
        try:
            object = bpy.data.objects.get(self.objectName)
            return BezierCurve.fromBlenderCurveData(object.data)
        except: return BezierCurve()
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass

    def getCopyValueFunctionString(self):
        return "return value.copy()"