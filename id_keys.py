import bpy
from mathutils import Vector
from bpy.props import *
from . utils.path import toIDPropertyPath as toPath


# ID Keys
##########################
    
def getIDKeyData(object, name, type = None):
    if not type: type = getIDType(name)
    typeClass = getIDTypeClass(type)
    return typeClass.read(object, name)
    
def getIDType(name):
    for keyName, keyType in getIDKeys():
        if name == keyName: return keyType    
    
def getIDTypeClass(type):
    return idTypes[type]    
    
def getIDKeys():
    scene = bpy.context.scene
    idKeys = getDefaultIDKeys()
    for item in scene.mn_settings.idKeys.keys:
        idKeys.append((item.name, item.type))
    return idKeys

def getDefaultIDKeys():
    return [("Initial Transforms", "Transforms")]    
    
 
def hasProp(object, name):
    return hasattr(object, toPath(name))
def getProp(object, name, default):
    return getattr(object, toPath(name), default)
def setProp(object, name, data):
    object[name] = data
    
    
    
# ID Types
############################  

# used for all custom id properties
prefix = "AN "  
    
class TransformsIDType:
    @classmethod
    def create(cls, object, name):
        cls.write(object, name, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    @staticmethod
    def exists(object, name):
        return hasProp(object, prefix + name + " Location") and \
               hasProp(object, prefix + name + " Rotation") and \
               hasProp(object, prefix + name + " Scale")

    @staticmethod
    def read(object, name):
        location = getProp(object, prefix + name + " Location", (0, 0, 0))
        rotation = getProp(object, prefix + name + " Rotation", (0, 0, 0))
        scale = getProp(object, prefix + name + " Scale", (1, 1, 1))
        
        return Vector(location), Vector(rotation), Vector(scale)
        
    @staticmethod
    def write(object, name, data):
        setProp(object, prefix + name + " Location", data[0])
        setProp(object, prefix + name + " Rotation", data[1])
        setProp(object, prefix + name + " Scale", data[2])
        
    @staticmethod
    def draw(layout, object, name):
        row = layout.row()
        
        col = row.column(align = True)
        col.label("Location")
        col.prop(object, toPath(prefix + name + " Location"), text = "")
        
        col = row.column(align = True)
        col.label("Rotation")
        col.prop(object, toPath(prefix + name + " Rotation"), text = "")
        
        col = row.column(align = True)
        col.label("Scale")
        col.prop(object, toPath(prefix + name + " Scale"), text = "")
        
    @staticmethod
    def drawOperators(layout, object, name):
        row = layout.row(align = True)
        props = row.operator("mn.set_current_transforms", text = "Use Current Transforms")
        props.name = name
        props.allSelectedObjects = False
        props = row.operator("mn.set_current_transforms", icon = "WORLD", text = "")
        props.name = name
        props.allSelectedObjects = True
        
        
class SimpleIDType:
    default = ""

    @classmethod
    def create(cls, object, name):
        cls.write(object, name, cls.default)

    @staticmethod
    def exists(object, name):
        return hasProp(object, prefix + name)

    @classmethod
    def read(cls, object, name):
        value = getProp(object, prefix + name, cls.default)
        return value
        
    @staticmethod
    def write(object, name, data):
        setProp(object, prefix + name, data)
        
    @classmethod
    def draw(cls, layout, object, name):
        layout.prop(object, toPath(prefix + name), text = "")      
        
        
class FloatIDType(SimpleIDType):
    default = 0.0

class StringIDType(SimpleIDType):
    default = ""
    
    @classmethod
    def draw(cls, layout, object, name):
        layout.prop(object, toPath(prefix + name), text = "")
        
        row = layout.row(align = True)
        props = row.operator("mn.set_current_texts", text = "Use Current Texts")
        props.name = name
        props.allSelectedObjects = False
        props = row.operator("mn.set_current_texts", icon = "WORLD", text = "")
        props.name = name
        props.allSelectedObjects = True

class IntegerIDType(SimpleIDType):
    default = 0     
        
        
idTypes = { "Transforms" : TransformsIDType,
            "Float" : FloatIDType,
            "String" : StringIDType,
            "Integer" : IntegerIDType } 
            
idTypeItems = [
    ("Transforms", "Transforms", "Contains 3 vectors for location, rotation and scale"),
    ("Float", "Float", "A single real number"),
    ("String", "String", "A text field"),
    ("Integer", "Integer", "Number without decimals") ]     
    
    
    
# Operators
##############################

class NewIdKey(bpy.types.Operator):
    bl_idname = "mn.new_id_key"
    bl_label = "New ID Key"
    bl_description = "New Key"
    
    @classmethod
    def poll(cls, context):
        name = cls.getNewKeyData()[0]
        return not cls.nameExists(name) and name != "" and "|" not in name
    
    def execute(self, context):
        name, type = self.getNewKeyData()
        idKeys = context.scene.mn_settings.idKeys
        item = idKeys.keys.add()
        item.name = name
        item.type = type
        context.area.tag_redraw()
        return {'FINISHED'}    
        
    @classmethod
    def nameExists(cls, name):
        return getIDType(name) is not None
        
    @classmethod
    def getNewKeyData(cls):
        idKeySettings = bpy.context.scene.mn_settings.idKeys
        return idKeySettings.new_key_name, idKeySettings.new_key_type
        
    
class RemoveIDKey(bpy.types.Operator):
    bl_idname = "mn.remove_id_key"
    bl_label = "Remove ID Key"
    bl_description = "Remove this key"
    
    name = StringProperty()
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        idKeys = context.scene.mn_settings.idKeys
        for i, item in enumerate(idKeys.keys):
            if item.name == self.name:
                idKeys.keys.remove(i)
        context.area.tag_redraw()
        return {'FINISHED'}
        
        
class CreateKeyOnObject(bpy.types.Operator):
    bl_idname = "mn.create_key_on_object"
    bl_label = "Create Key on Object"
    bl_description = ""
    
    name = StringProperty()
    type = StringProperty()
    objectName = StringProperty()
    
    def execute(self, context):
        typeClass = getIDTypeClass(self.type)
        typeClass.create(bpy.data.objects.get(self.objectName), self.name)
        context.area.tag_redraw()
        return {'FINISHED'}
        
        
class SetCurrentTransforms(bpy.types.Operator):
    bl_idname = "mn.set_current_transforms"
    bl_label = "Set Current Transforms"
    bl_description = "Set current transforms (World icon means to do this for all selected objects)"
    
    name = StringProperty()
    allSelectedObjects = BoolProperty()
    
    def execute(self, context):
        if self.allSelectedObjects: objects = context.selected_objects
        else: objects = [context.active_object]
        
        for object in objects:
            TransformsIDType.write(object, self.name, (object.location, object.rotation_euler, object.scale))
        return {'FINISHED'}
        
        
class SetCurrentTexts(bpy.types.Operator):
    bl_idname = "mn.set_current_texts"
    bl_label = "Set Current Texts"
    bl_description = "Set current texts (World icon means to do this for all selected objects)"
    
    name = StringProperty()
    allSelectedObjects = BoolProperty()
    
    def execute(self, context):
        if self.allSelectedObjects: objects = context.selected_objects
        else: objects = [context.active_object]
        
        for object in objects:
            StringIDType.write(object, self.name, getattr(object.data, "body", ""))
        return {'FINISHED'} 