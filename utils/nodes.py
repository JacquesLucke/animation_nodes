import bpy

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
