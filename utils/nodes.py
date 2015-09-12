import bpy

def newNodeAtCursor(type):
    bpy.ops.node.add_and_link_node(type = type)
    return bpy.context.space_data.node_tree.nodes[-1]

def invokeTranslation():
    bpy.ops.node.translate_attach("INVOKE_DEFAULT")

def idToSocket(socketID):
    return getSocket(socketID[0][0], socketID[0][1], socketID[1], socketID[2])

def idToNode(nodeID):
    return getNode(*nodeID)


def getSocket(treeName, nodeName, isOutput, identifier):
    node = getNode(treeName, nodeName)
    sockets = node.outputs if isOutput else node.inputs
    for socket in sockets:
        if socket.identifier == identifier: return socket

def getNode(treeName, nodeName):
    return bpy.data.node_groups[treeName].nodes[nodeName]

def iterAnimationNodes():
    for nodeTree in getAnimationNodeTrees():
        for node in nodeTree.nodes:
            if getattr(node, "isAnimationNode", False):
                yield node

def getAnimationNodeTrees():
    nodeTrees = []
    for nodeTree in bpy.data.node_groups:
        if nodeTree.bl_idname == "an_AnimationNodeTree":
            nodeTrees.append(nodeTree)
    return nodeTrees

def getAnimationNodeClasses():
    from .. base_types.node import AnimationNode
    return AnimationNode.__subclasses__()
