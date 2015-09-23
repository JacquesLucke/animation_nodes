import bpy
from bpy.props import *
from .. utils.nodes import getNode
from .. sockets.info import toDataType

'''
                ###############

    #########                      Second active node suggestion

 Data Input                               First active node suggestion

    #########                      All other active node suggestions

                  Debug Node

How to implement suggestions on a per node basis:
1. Create a 'getNextNodeSuggestions(self)' function inside the node
2. Return a list that looks like this:
    [("an_FloatMathNode", (0, 0)),                      # First suggestion
     ("an_CombineVector", (0, 0)),                      # Second suggestion
     ("an_FloatClamp", (0, 0)),                         # ... can be an unlimited amount of suggestions
     ("an_CombineVector", (0, 0), (0, 1), (0, 2))]      # the tuples indicate which sockets to connect: (output index, input index)
'''

class ContextPie(bpy.types.Menu):
    bl_idname = "an.context_pie"
    bl_label = "Context Pie"

    @classmethod
    def poll(cls, context):
        return animationNodeTreeActive()

    def drawLeft(self, context, layout):
        if activeNodeHasInputs():
            layout.operator("an.insert_data_input_node_template_operator", text = "Data Input")
        else:
            self.empty(layout)

    def drawRight(self, context, layout):
        if len(self.activeNodeSuggestions) > 0:
            self.drawInsertNodeOperator(layout, self.activeNodeSuggestions[0])
        else:
            self.empty(layout)

    def drawBottom(self, context, layout):
        if activeNodeHasOutputs():
            layout.operator("an.insert_debug_node_template_operator", text = "Debug")
        else:
            self.empty(layout)

    def drawTop(self, context, layout):
        self.empty(layout)

    def drawTopLeft(self, context, layout):
        self.empty(layout)

    def drawTopRight(self, context, layout):
        if len(self.activeNodeSuggestions) > 1:
            self.drawInsertNodeOperator(layout, self.activeNodeSuggestions[1])
        else:
            self.empty(layout)

    def drawBottomLeft(self, context, layout):
        self.empty(layout)

    def drawBottomRight(self, context, layout):
        amount = len(self.activeNodeSuggestions)
        if amount == 3:
            self.drawInsertNodeOperator(layout, self.activeNodeSuggestions[2])
        elif amount > 3:
            col = layout.column()
            for suggestion in self.activeNodeSuggestions[2:]:
                self.drawInsertNodeOperator(col, suggestion)
        else:
            self.empty(layout)


    def draw(self, context):
        self.prepare(context)

        pie = self.layout.menu_pie()
        self.drawLeft(context, pie)
        self.drawRight(context, pie)
        self.drawBottom(context, pie)
        self.drawTop(context, pie)
        self.drawTopLeft(context, pie)
        self.drawTopRight(context, pie)
        self.drawBottomLeft(context, pie)
        self.drawBottomRight(context, pie)

    def prepare(self, context):
        node = context.active_node
        try: self.activeNodeSuggestions = node.getNextNodeSuggestions()
        except: self.activeNodeSuggestions = []

    def empty(self, layout):
        layout.row().label("")

    def drawInsertNodeOperator(self, layout, data):
        nodeIdName = data[0]
        links = data[1:]

        props = layout.operator("an.insert_linked_node", text = getNodeNameFromIdName(nodeIdName))
        props.nodeType = nodeIdName
        for origin, target in links:
            item = props.links.add()
            item.origin = origin
            item.target = target


def getNodeNameFromIdName(idName):
    try: return getattr(bpy.types, idName).bl_label
    except: return ""

def activeNodeHasOutputs():
    if not activeNodeExists(): return False
    node = getActiveNode()
    return len(node.outputs) > 0

def activeNodeHasInputs():
    if not activeNodeExists(): return False
    node = getActiveNode()
    return len(node.inputs) > 0

def activeNodeExists():
    try: return getActiveNode() is not None
    except: return False

def getActiveNode():
    return getattr(bpy.context, "active_node", None)

def animationNodeTreeActive():
    try: return getActiveAnimationNodeTree() is not None
    except: return False

def getActiveAnimationNodeTree():
    try:
        nodeTree = bpy.context.space_data.edit_tree
        if nodeTree.bl_idname == "an_AnimationNodeTree": return nodeTree
    except: pass
    return None
