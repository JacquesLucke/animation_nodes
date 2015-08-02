import bpy
import random
from bpy.props import *
from bpy.app.handlers import persistent
from . node_function_call import getNodeFunctionCallOperatorName
from .. utils.mn_node_utils import getAnimationNodeTrees

class AnimationNode:
    identifier = StringProperty(name = "Identifier", default = "")

    searchTags = []
    onlySearchTags = False
    isDetermined = False

    @classmethod
    def poll(cls, nodeTree):
        return nodeTree.bl_idname == "mn_AnimationNodeTree"

    # On creation
    def init(self, context):
        self.identifier = createIdentifier()
        self.create()

    def create(self):
        '''Implement this in all subclasses'''
        pass

    # On node tree changes
    def update(self):
        '''Don't use this function at all'''
        pass

    def edit(self):
        """Optional function for subclasses"""
        pass

    # On node duplication
    def copy(self, sourceNode):
        self.identifier = createIdentifier()
        self.duplicate(sourceNode)

    def duplicate(self, sourceNode):
        """Optional function for subclasses"""
        pass

    # On node deletion
    def free(self):
        self.delete()

    def delete(self):
        """Optional function for subclasses"""
        pass


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
