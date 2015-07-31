import bpy
from bpy.props import *
from . node_function_call import getNodeFunctionCallOperatorName
from .. utils.mn_node_utils import getNode

class AnimationNode:
    @classmethod
    def poll(cls, nodeTree):
        return nodeTree.bl_idname == "mn_AnimationNodeTree"

    def init(self, context):
        self.id_data.startEdit()
        self.create()
        self.id_data.stopEdit()

    def update(self):
        return

    def copy(self, sourceNode):
        self.id_data.startEdit()
        if hasattr(self, "duplicate"):
            self.duplicate(sourceNode)
        self.id_data.stopEdit()

    def free(self):
        self.id_data.startEdit()
        if hasattr(self, "delete"):
            self.delete()
        self.id_data.stopEdit()

    def callFunctionFromUI(self, layout, functionName, text = "", icon = "NONE", description = ""):
        idName = getNodeFunctionCallOperatorName(description)
        props = layout.operator(idName, text = text, icon = icon)
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name
        props.functionName = functionName
