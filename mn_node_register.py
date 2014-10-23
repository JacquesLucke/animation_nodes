import bpy
from mn_node_list import getNodeNameDictionary
from nodeitems_utils import NodeCategory, NodeItem
from nodeitems_utils import register_node_categories, unregister_node_categories

class AnimationNodesCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'AnimationNodeTreeType'
		
def getAllNodeIdNames():
	nodeDictionary = getNodeNameDictionary()
	nodeIdNames = []
	for (categoryName, nodeNames) in nodeDictionary:
		nodeItems = []
		for nodeData in nodeNames:
			nodeIdNames.append(nodeData[0])
	return nodeIdNames

def getNodeCategories():
	nodeDictionary = getNodeNameDictionary()
	nodeCategories = []
	for (categoryName, nodeNames) in nodeDictionary:
		nodeItems = []
		for nodeData in nodeNames:
			nodeItems.append(NodeItem(nodeData[0], label = nodeData[1]))
		category = AnimationNodesCategory(categoryName.upper(), categoryName, items = nodeItems)
		nodeCategories.append(category)
	return nodeCategories