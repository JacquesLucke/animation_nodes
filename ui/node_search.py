import bpy
import itertools
from bpy.props import *
from .. node_creator import NodeCreator
from .. utils.enum_items import enumItemsFromDicts
from .. utils.nodes import getAnimationNodeClasses

itemsByIdentifier = {}

@enumItemsFromDicts
def getSearchItems(self, context):
    itemsByIdentifier.clear()
    items = []
    for item in itertools.chain(iterSingleNodeItems(), iterTemplateItems()):
        itemsByIdentifier[item.identifier] = item
        items.append({"id" : item.identifier, "name" : item.searchTag})
    return items

class NodeSearch(bpy.types.Operator):
    bl_idname = "an.node_search"
    bl_label = "Node Search"
    bl_options = {"REGISTER"}
    bl_property = "item"

    item = EnumProperty(items = getSearchItems)

    @classmethod
    def poll(cls, context):
        try: return context.space_data.node_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}

    def execute(self, context):
        itemsByIdentifier[self.item].insert()
        return {"FINISHED"}


class InsertItem:
    @property
    def identifier(self):
        return ""

    @property
    def searchTag(self):
        return ""

    def insert(self):
        pass



# Single Nodes
#################################

def iterSingleNodeItems():
    for node in getAnimationNodeClasses():
        if not node.onlySearchTags:
            yield SingleNodeInsertionItem(node.bl_idname, node.bl_label)
        for customSearch in node.getSearchTags():
            if isinstance(customSearch, tuple):
                yield SingleNodeInsertionItem(node.bl_idname, customSearch[0], customSearch[1])
            else:
                yield SingleNodeInsertionItem(node.bl_idname, customSearch)

class SingleNodeInsertionItem:
    def __init__(self, idName, tag, settings = {}):
        self.idName = idName
        self.tag = tag
        self.settings = settings

    @property
    def identifier(self):
        return "single node - " + self.tag

    @property
    def searchTag(self):
        return self.tag

    def insert(self):
        InsertSingleNode(self.idName, self.settings)

class InsertSingleNode(NodeCreator):
    def insert(self, idName, settings):
        node = self.newNode(idName)
        for key, value in settings.items():
            setattr(node, key, eval(value))



# Templates
#################################

def iterTemplateItems():
    for template in getNodeTemplates():
        print(template)
        yield TemplateInsertionItem(template, template.label)

def getNodeTemplates():
    return [template for template in NodeCreator.__subclasses__() if hasattr(template, "label")]

class TemplateInsertionItem:
    def __init__(self, template, tag):
        self.template = template
        self.tag = tag

    @property
    def identifier(self):
        return "template - " + self.tag

    @property
    def searchTag(self):
        return self.tag + " - Template"

    def insert(self):
        self.template()
