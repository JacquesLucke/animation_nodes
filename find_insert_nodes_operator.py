import bpy
from collections import defaultdict
from . utils.mn_node_utils import getAnimationNodeTrees

searchDict = {}
importanceMap = defaultdict(int)

def getItems(self, context):
    def getSortKey(item):
        key = str(10000 - importanceMap[item[0]]).zfill(5) + item[1]
        return key
    updateSearchDict()
    items = []
    for key in searchDict.keys():
        items.append((key, key, ""))
    items = sorted(items, key = getSortKey)
    return items

class InsertNodeOperator(bpy.types.Operator):
    bl_idname = "mn.insert_node"
    bl_label = "Find and Insert Node"
    bl_options = {"REGISTER"}
    bl_property = "item"

    item = bpy.props.EnumProperty(items = getItems)

    def invoke(self, context, event):
        if getNodeTree():
            context.window_manager.invoke_search_popup(self)
        else:
            context.window_manager.popup_menu(drawNodeTreeChooser, title = "Select Node Tree")
        return {"CANCELLED"}

    def execute(self, context):
        nodeType, settings = searchDict[self.item]
        bpy.ops.node.add_and_link_node("INVOKE_DEFAULT", type = nodeType, use_transform = True, settings = settings)
        importanceMap[self.item] += 1
        return {"FINISHED"}

def drawNodeTreeChooser(self, context):
    layout = self.layout
    nodeTrees = getAnimationNodeTrees()
    if len(nodeTrees) == 0:
        layout.operator("mn.create_node_tree", text = "New Node Tree", icon = "PLUS")
    else:
        for nodeTree in nodeTrees:
            props = layout.operator("mn.select_node_tree", text = "Select '{}'".format(nodeTree.name), icon = "EYEDROPPER")
            props.nodeTreeName = nodeTree.name

def getNodeTree():
    return getattr(bpy.context.space_data, "node_tree", None)

def updateSearchDict():
    global searchDict
    searchDict = {}

    for cls in getNodeClasses():
        tags = []
        if not cls.onlySearchTags: tags.append(cls.bl_label)
        tags.extend(cls.searchTags)
        # each tag contains either only a name or a name and a settings dictionary
        for tag in tags:
            if isinstance(tag, str):
                searchDict[tag] = (cls.bl_idname, [])
            else:
                searchDict[tag[0]] = (cls.bl_idname, createSettingsPropertyGroup(tag[1]))

def createSettingsPropertyGroup(easyDict):
    settings = []
    for key, value in easyDict.items():
        settings.append({"name" : key, "value" : value})
    return settings

def getNodeClasses():
    from . base_types.node import AnimationNode
    return AnimationNode.__subclasses__()
