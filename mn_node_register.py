import bpy
from . nodes.mn_node_list import getNodeNameDictionary
from nodeitems_utils import NodeCategory, NodeItem, _node_categories
from nodeitems_utils import register_node_categories, unregister_node_categories

class AnimationNodesCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'mn_AnimationNodeTree'
        
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
            if len(nodeData) == 2:
                nodeItems.append(NodeItem(nodeData[0], label = nodeData[1]))
            elif len(nodeData) == 3:
                nodeItems.append(NodeItem(nodeData[0], label = nodeData[1], settings = nodeData[2]))
        category = AnimationNodesCategory(categoryName.upper(), categoryName, items = nodeItems)
        nodeCategories.append(category)
    return nodeCategories
    
def register_node_menu():
    categories = getNodeCategories()
    unregister_node_menu()
    register_node_categories("ANIMATIONNODES", categories)
    
def unregister_node_menu():
    if "ANIMATIONNODES" in _node_categories:
        unregister_node_categories("ANIMATIONNODES")