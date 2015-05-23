import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *
from .. data_structures.splines.from_blender import createSplinesFromBlenderObject

class mn_SplineListSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_SplineListSocket"
    bl_label = "Spline List Socket"
    dataType = " Spline List"
    allowedInputTypes = ["Spline List"]
    drawColor = (0.5, 0.28, 1.0, 1.0)
    
    objectName = bpy.props.StringProperty(default = "", description = "Use the splines from this object", update = nodePropertyChanged)
    showName = bpy.props.BoolProperty(default = True)
    useWorldSpace = bpy.props.BoolProperty(default = True, description = "Convert points to world space", update = nodePropertyChanged)
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
            row.prop(self, "useWorldSpace", text = "", icon = "WORLD")
        
    def getValue(self):
        object = bpy.data.objects.get(self.objectName)
        splines = createSplinesFromBlenderObject(object)
        if self.useWorldSpace:
            for spline in splines:
                spline.transform(object.matrix_world)
        return splines
        
    def setStoreableValue(self, data):
        self.objectName, self.useWorldSpace = data
    def getStoreableValue(self):
        return (self.objectName, self.useWorldSpace)
        
    def getCopyValueFunctionString(self):
        return "return [element.copy() for element in value]"
