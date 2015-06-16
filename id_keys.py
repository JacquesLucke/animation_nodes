import bpy
from mathutils import Vector
from bpy.props import *
from . utils.path import toIDPropertyPath as toPath


# ID Keys
##########################

forcedIDKeyTypes = {
    "Initial Transforms" : "Transforms",
    "Initial Text" : "String" }
    
def getIDKeyData(object, name, type = None):
    if not type: type = getIDType(name)
    typeClass = getIDTypeClass(type)
    return typeClass.read(object, name)
    
def setIDKeyData(object, name, type, data):
    typeClass = getIDTypeClass(type)
    typeClass.write(object, name, data)
    
def getIDType(name):
    for item in getIDKeys():
        if name == item.name: return item.type    
    
def getIDTypeClass(type):
    return idTypes[type]    
    
def getIDKeys():
    return getIDKeySettings().keys
    
def getIDKeySettings():
    return bpy.context.scene.mn_settings.idKeys

    
def createIDKey(name, type):
    if not isCreatable(name, type): return
    idKeys = getIDKeys()
    item = idKeys.add()
    item.name = name
    item.type = type
    
def isCreatable(name, type):
    if idKeyExists(name): return False
    if not isValidCombination(name, type): return False
    return True
    
def idKeyExists(name):
    for item in getIDKeys():
        if item.name == name: return True
    return False
    
def isValidCombination(name, type):
    if "|" in name: return False
    if "|" in type: return False
    if name in forcedIDKeyTypes:
        if forcedIDKeyTypes[name] != type: return False
    return True
    
 
def hasProp(object, name):
    return hasattr(object, toPath(name))
def getProp(object, name, default):
    return getattr(object, toPath(name), default)
def setProp(object, name, data):
    object[name] = data
def removeProp(object, name):
    if hasProp(object, name):
        del object[name]
    
    
    
# ID Types
############################  

# used for all custom id properties
prefix = "AN "  
    
class TransformsIDType:
    @classmethod
    def create(cls, object, name):
        cls.write(object, name, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))
        
    @staticmethod
    def remove(object, name):
        removeProp(object, prefix + name + " Location")
        removeProp(object, prefix + name + " Rotation")
        removeProp(object, prefix + name + " Scale")

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
    def remove(object, name):
        removeProp(object, prefix + name)

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

    @staticmethod
    def drawOperators(layout, object, name):
        pass
        
        
class FloatIDType(SimpleIDType):
    default = 0.0

class StringIDType(SimpleIDType):
    default = ""
    
    @classmethod
    def draw(cls, layout, object, name):
        layout.prop(object, toPath(prefix + name), text = "")
        
    @staticmethod
    def drawOperators(layout, object, name):
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
    
    
    
# Panels
##############################

class IDKeysManagerPanel(bpy.types.Panel):
    bl_idname = "mn.id_keys_manager"
    bl_label = "ID Keys Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "AN"
        
    def draw(self, context):
        layout = self.layout
        self.drawExistingKeysBox(layout)
        self.drawNewKeyRow(layout)
        
    def drawExistingKeysBox(self, layout):
        box = layout.box()
        idKeys = getIDKeys()
        if len(idKeys) == 0:
            box.label("There is no ID Key")
        for item in idKeys:
            row = box.row()
            row.label(item.name)
            row.label(item.type)
            hideIcon = "RESTRICT_VIEW_ON" if item.hide else "RESTRICT_VIEW_OFF"
            row.prop(item, "hide", icon = hideIcon, emboss = False, icon_only = True)
            props = row.operator("mn.remove_id_key", icon = "X", text = "")
            props.name = item.name
            
    def drawNewKeyRow(self, layout):
        idKeySettings = bpy.context.scene.mn_settings.idKeys   
        row = layout.row(align = True)
        row.prop(idKeySettings, "newKeyName", text = "")
        row.prop(idKeySettings, "newKeyType", text = "")
        row.operator("mn.new_id_key", icon = "PLUS", text = "")
        
        
class IDKeyPanel(bpy.types.Panel):
    bl_idname = "mn.id_keys"
    bl_label = "ID Keys for Active Object"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "AN"
        
    @classmethod
    def poll(cls, context):
        return context.active_object
        
    def draw(self, context):
        layout = self.layout
        object = context.active_object
        
        for item in getIDKeys():
            keyName, keyType = item.name, item.type
            
            typeClass = getIDTypeClass(keyType)
            keyExists = typeClass.exists(object, keyName)
        
            box = layout.box()
            self.drawHeader(box, object, keyName, keyType, keyExists)
            
            if keyExists:
                typeClass.draw(box, object, keyName)
            typeClass.drawOperators(box, object, keyName)    
    
    def drawHeader(self, box, object, keyName, keyType, keyExists):
        row = box.row()
        
        subRow = row.row()
        subRow.alignment = "LEFT"
        subRow.label(keyName)
        
        subRow = row.row()
        subRow.alignment = "RIGHT"
        subRow.label(keyType)
        
        if keyExists:
            props = row.operator("mn.remove_key_from_object", icon = "X", emboss = False, text = "")
        else:
            props = row.operator("mn.create_key_on_object", icon = "NEW", emboss = False,  text = "")
        props.name = keyName
        props.type = keyType
        props.objectName = object.name
        
        
    
    
# Operators
##############################

class NewIdKey(bpy.types.Operator):
    bl_idname = "mn.new_id_key"
    bl_label = "New ID Key"
    bl_description = "New Key"
    
    @classmethod
    def poll(cls, context):
        name, type = cls.getNewKeyData()
        return isCreatable(name, type)
    
    def execute(self, context):
        name, type = self.getNewKeyData()
        createIDKey(name, type)
        getIDKeySettings().newKeyName = ""
        context.area.tag_redraw()
        return {'FINISHED'}
        
    @classmethod
    def getNewKeyData(cls):
        idKeySettings = getIDKeySettings()
        return idKeySettings.newKeyName, idKeySettings.newKeyType
        
    
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
        
        
class RemoveKeyFromObject(bpy.types.Operator):
    bl_idname = "mn.remove_key_from_object"
    bl_label = "Remove Key from Object"
    bl_description = ""
    
    name = StringProperty()
    type = StringProperty()
    objectName = StringProperty()
    
    def execute(self, context):
        typeClass = getIDTypeClass(self.type)
        typeClass.remove(bpy.data.objects.get(self.objectName), self.name)
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