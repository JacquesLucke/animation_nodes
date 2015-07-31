import bpy
import random
from bpy.props import *
from bpy.app.handlers import persistent
from . node_function_call import getNodeFunctionCallOperatorName
from .. utils.mn_node_utils import getAnimationNodeTrees

class AnimationNode:
    identifier = StringProperty(name = "Identifier", default = "")

    @classmethod
    def poll(cls, nodeTree):
        return nodeTree.bl_idname == "mn_AnimationNodeTree"

    def init(self, context):
        self.identifier = createIdentifier()
        self.id_data.startEdit()
        self.create()
        self.id_data.stopEdit()

    def update(self):
        return

    def copy(self, sourceNode):
        self.identifier = createIdentifier()
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

@persistent
def createMissingIdentifiers(scene = None):
    def unidentifiedNodes():
        for tree in getAnimationNodeTrees():
            for node in tree.nodes:
                if not issubclass(type(node), AnimationNode): continue
                if node.identifier == "": yield node

    for node in unidentifiedNodes():
        node.identifier = createIdentifier()

def createIdentifier():
    identifierLength = 15
    characters = "abcdefghijklmnopqrstuvwxyz" + "0123456789"
    return ''.join(random.choice(characters) for _ in range(identifierLength))



# Register
##################################

def register_handlers():
    bpy.app.handlers.load_post.append(createMissingIdentifiers)

def unregister_handlers():
    bpy.app.handlers.load_post.remove(createMissingIdentifiers)
