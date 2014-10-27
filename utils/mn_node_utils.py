import bpy

def getNodeFromTypeWithAttribute(nodeType, attribute, data):
	nodes = getNodesFromTypeWithAttribute(nodeType, attribute, data)
	if len(nodes) > 0: return nodes[0]
	return None

def getNodesFromTypeWithAttribute(nodeType, attribute, data):
	nodes = []
	nodesFromType = getNodesFromType(nodeType)
	for node in nodesFromType:
		if getattr(node, attribute) == data:
			nodes.append(node)
	return nodes

def getNodesFromType(nodeType):
	nodes = []
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:
		for node in nodeTree.nodes:
			if node.bl_idname == nodeType:
				nodes.append(node)
	return nodes
	
def getAnimationNodeTrees():
	nodeTrees = []
	for nodeTree in bpy.data.node_groups:
		if hasattr(nodeTree, "isAnimationNodeTree"):
			nodeTrees.append(nodeTree)
	return nodeTrees