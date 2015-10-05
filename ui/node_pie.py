import bpy
from bpy.props import *
from .. utils.nodes import getNode
from .. sockets.info import toDataType

'''
                ###############

    #########                      #########

 Data Input                               #########

    #########                      #########

                  Debug Node

'''

class ContextPie(bpy.types.Menu):
    bl_idname = "an.context_pie"
    bl_label = "Context Pie"

    @classmethod
    def poll(cls, context):
        try: return context.active_node.isAnimationNode
        except: return False

    def drawLeft(self, layout):
        amount = len(self.activeNode.getVisibleInputs())
        if amount == 0: self.empty(layout, text = "Has no visible inputs")
        else: layout.operator("an.insert_data_input_node_template_operator", text = "Data Input")

    def drawRight(self, layout):
        self.empty(layout)

    def drawBottom(self, layout):
        amount = len(self.activeNode.getVisibleOutputs())
        if amount == 0: self.empty(layout, text = "Has no visible outputs")
        else: layout.operator("an.insert_debug_node_template_operator", text = "Debug")

    def drawTop(self, layout):
        self.empty(layout)

    def drawTopLeft(self, layout):
        self.empty(layout)

    def drawTopRight(self, layout):
        self.empty(layout)

    def drawBottomLeft(self, layout):
        self.empty(layout)

    def drawBottomRight(self, layout):
        self.empty(layout)


    def draw(self, context):
        pie = self.layout.menu_pie()
        self.drawLeft(pie)
        self.drawRight(pie)
        self.drawBottom(pie)
        self.drawTop(pie)
        self.drawTopLeft(pie)
        self.drawTopRight(pie)
        self.drawBottomLeft(pie)
        self.drawBottomRight(pie)

    def empty(self, layout, text = ""):
        layout.row().label(text)

    @property
    def activeNode(self):
        return bpy.context.active_node
