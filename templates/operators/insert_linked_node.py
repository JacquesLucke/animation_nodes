import bpy
from bpy.props import *
from bl_operators.node import NodeSetting
from ... base_types.template import Template

class NodeSetting(bpy.types.PropertyGroup):
    value = StringProperty()

class InsertLinkedNodeOperatorTemplate(bpy.types.Operator, Template):
    bl_idname = "an.insert_linked_node_operator_template"
    bl_label = "Insert Linked Node"

    nodeIdName = StringProperty()
    settings = CollectionProperty(name = "Settings", type = NodeSetting, options = {"SKIP_SAVE"})
    fromIndex = IntProperty(default = 0)
    toIndex = IntProperty(default = 0)

    def insert(self):
        activeNode = self.activeNode
        node = self.newNode(self.nodeIdName)

        for setting in self.settings:
            value = eval(setting.value)
            setattr(node, setting.name, value)

        activeNode.outputs[self.fromIndex].linkWith(node.inputs[self.toIndex])
        self.setActiveNode(node)

def invokeLinkedNodeInsertion(layout, idName, fromIndex, toIndex, text, settings = {}):
    props = layout.operator("an.insert_linked_node_operator_template", text = text)
    props.nodeIdName = idName
    props.fromIndex = fromIndex
    props.toIndex = toIndex

    for name, value in settings.items():
        item = props.settings.add()
        item.name = name
        item.value = value
