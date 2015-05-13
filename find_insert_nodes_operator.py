import bpy
from collections import defaultdict

searchDict = {}
importanceMap = defaultdict(int)

def getItems(self, context):
    def getSortKey(item):
        key = str(10000 - importanceMap[item[0]]).zfill(5) + item[1]
        return key
    updateSearchDict()
    items = []
    for key, value in searchDict.items():
        items.append((value, key, ""))
    items = sorted(items, key = getSortKey)
    return items

class InsertNodeOperator(bpy.types.Operator):
    bl_idname = "mn.insert_node"
    bl_label = "Find and Insert Node"
    bl_options = {"REGISTER"}
    bl_property = "item"
    
    item = bpy.props.EnumProperty(items = getItems)
    
    @classmethod
    def poll(cls, context):
        return getNodeTree()
    
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}
        
    def execute(self, context):
        bpy.ops.node.add_and_link_node("INVOKE_DEFAULT", type = self.item, use_transform = True)
        importanceMap[self.item] += 1
        return {"FINISHED"}
    
def getNodeTree():
    return getattr(bpy.context.space_data, "node_tree", None)
   
def updateSearchDict():
    global searchDict
    searchDict = {}
    
    for cls in getNodeClasses():
        tags = []
        tags.append(cls.bl_label)
        tags.extend(getattr(cls, "search_tags", []))
        for tag in tags:
            searchDict[tag] = cls.bl_idname
        
def getNodeClasses():
    from . mn_node_base import AnimationNode
    return AnimationNode.__subclasses__()