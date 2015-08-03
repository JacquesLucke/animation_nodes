import bpy
from bpy.props import *
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_ObjectSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_ObjectSocket"
    bl_label = "Object Socket"
    dataType = "Object"
    allowedInputTypes = ["Object"]
    drawColor = (0, 0, 0, 1)
    
    objectName = StringProperty(update = nodePropertyChanged)
    showName = BoolProperty(default = True)
    objectCreationType = StringProperty(default = "")
    
    def drawInput(self, layout, node, text):
        col = layout.column()
        row = col.row(align = True)
        if self.showName:
            row.label(text)
        row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = "")
        
        if self.objectCreationType != "":
            creator = row.operator("mn.assign_new_empty_mesh_object_to_socket", text = "", icon = "PLUS")
            creator.nodeTreeName = node.id_data.name
            creator.nodeName = node.name
            creator.isOutput = self.is_output
            creator.socketName = self.name
            creator.objectType = self.objectCreationType
        
        selector = row.operator("mn.assign_active_object_to_socket", text = "", icon = "EYEDROPPER")
        selector.nodeTreeName = node.id_data.name
        selector.nodeName = node.name
        selector.isOutput = self.is_output
        selector.socketName = self.name
        selector.target = "objectName"
        
    def getValue(self):
        return bpy.data.objects.get(self.objectName)
        
    def setStoreableValue(self, data):
        self.objectName = data
    def getStoreableValue(self):
        return self.objectName
    
    
class AssignActiveObjectToNode(bpy.types.Operator):
    bl_idname = "mn.assign_active_object_to_socket"
    bl_label = "Assign Active Object"
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    target = bpy.props.StringProperty()
    isOutput = bpy.props.BoolProperty()
    socketName = bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        return getActive() is not None
        
    def execute(self, context):
        obj = getActive()
        node = getNode(self.nodeTreeName, self.nodeName)
        socket = getSocketFromNode(node, self.isOutput, self.socketName)
        setattr(socket, self.target, obj.name)
        return {'FINISHED'}

class CreateEmptyMeshObject(bpy.types.Operator):
    bl_idname = "mn.assign_new_empty_mesh_object_to_socket"
    bl_label = "Create Empty Mesh Object"
    bl_description = "Create new object and assign to this socket"
    bl_options = {"REGISTER"}
    
    nodeTreeName = StringProperty()
    nodeName = StringProperty()
    isOutput = BoolProperty()
    socketName = StringProperty()
    
    objectType = StringProperty()
    
    def execute(self, context):
        data = None
        if self.objectType == "MESH": data = bpy.data.meshes.new("Mesh")
        if self.objectType == "CURVE": 
            data = bpy.data.curves.new("Curve", "CURVE")
            data.dimensions = "3D"
            data.fill_mode = "FULL"
        object = bpy.data.objects.new("Target", data)
        context.scene.objects.link(object)
        
        node = getNode(self.nodeTreeName, self.nodeName)
        socket = getSocketFromNode(node, self.isOutput, self.socketName)
        socket.objectName = object.name
        return {"FINISHED"}        