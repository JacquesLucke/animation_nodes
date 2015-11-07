import bpy

def newNodeAtCursor(type):
    bpy.ops.node.add_and_link_node(type = type)
    return bpy.context.space_data.node_tree.nodes[-1]

def invokeTranslation():
    bpy.ops.node.translate_attach("INVOKE_DEFAULT")

def idToSocket(socketID):
    node = bpy.data.node_groups[socketID[0][0]].nodes[socketID[0][1]]
    identifier = socketID[2]
    sockets = node.outputs if socketID[1] else node.inputs
    for socket in sockets:
        if socket.identifier == identifier: return socket

def idToNode(nodeID):
    return bpy.data.node_groups[nodeID[0]].nodes[nodeID[1]]


def getSocket(treeName, nodeName, isOutput, identifier):
    node = bpy.data.node_groups[treeName].nodes[nodeName]
    sockets = node.outputs if isOutput else node.inputs
    for socket in sockets:
        if socket.identifier == identifier: return socket

def getNode(treeName, nodeName):
    return bpy.data.node_groups[treeName].nodes[nodeName]

def iterAnimationNodes():
    for nodeTree in getAnimationNodeTrees():
        for node in nodeTree.nodes:
            if node.isAnimationNode: yield node

def getAnimationNodeTrees(skipLinkedTrees = True):
    nodeTrees = []
    for nodeTree in bpy.data.node_groups:
        if nodeTree.bl_idname != "an_AnimationNodeTree": continue
        if skipLinkedTrees and nodeTree.library is not None: continue
        nodeTrees.append(nodeTree)
    return nodeTrees

def getAnimationNodeClasses():
    from .. base_types.node import AnimationNode
    return AnimationNode.__subclasses__()
