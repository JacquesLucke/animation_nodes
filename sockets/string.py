import bpy
from bpy.props import *
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *

class EnumItem(bpy.types.PropertyGroup):
    displayName = StringProperty()
    identifier = StringProperty()
    description = StringProperty(default = "")
    icon = StringProperty(default = "NONE")

class mn_StringSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_StringSocket"
    bl_label = "String Socket"
    dataType = "String"
    allowedInputTypes = ["String"]
    drawColor = (1, 1, 1, 1)
    
    def getEnumItems(self, context):
        items = []
        for i, item in enumerate(self.enumItems):
            items.append((item.identifier, item.displayName, item.description, item.icon, i))
        if len(items) == 0: items.append(("NONE", "NONE", ""))
        return items
        
    def enumChanged(self, context):
        if self.useEnum:
            self.value = self.stringEnum
    
    value = StringProperty(default = "", update = nodePropertyChanged)
    showName = BoolProperty(default = True)
    stringEnum = EnumProperty(items = getEnumItems, name = "Possible Items", update = enumChanged)
    useEnum = BoolProperty(default = False)
    enumItems = CollectionProperty(type = EnumItem)
    
    def drawInput(self, layout, node, text):
        if not self.showName: text = ""
        if self.useEnum:
            layout.prop(self, "stringEnum", text = text)
        else:
            layout.prop(self, "value", text = text)
        
    def getValue(self):
        return self.value
        
    def setStoreableValue(self, data):
        self.value = data
    def getStoreableValue(self):
        return self.value

    def setEnumItems(self, enumItems):
        self.enumItems.clear()
        for enumItem in enumItems:
            item = self.enumItems.add()
            item.identifier = enumItem[0]
            if len(enumItem) > 1: item.displayName = enumItem[1]
            else: item.displayName = enumItem[0]
            if len(enumItem) > 2: item.description = enumItem[2]
            if len(enumItem) > 3: item.icon = enumItem[3]