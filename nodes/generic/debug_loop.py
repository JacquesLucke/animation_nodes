import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... tree_info import getNodesByType

class DebugLoopNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DebugLoopNode"
    bl_label = "Debug Loop"

    textBlockName = StringProperty(name = "Text")

    def create(self):
        self.newInput("Node Control", "...", "control")
        self.newInputSocket()

    def edit(self):
        controlSocket = self.inputs[-1]
        directOrigin = controlSocket.directOrigin
        if directOrigin is None: return
        socket = self.newInputSocket()
        socket.linkWith(directOrigin)
        controlSocket.removeLinks()

    def newInputSocket(self):
        socket = self.newInput("an_GenericSocket", "Data", "data")
        socket.removeable = True
        socket.moveable = True
        socket["dataWidth"] = 10
        socket.moveUp()
        return socket

    def draw(self, layout):
        layout.prop_search(self, "textBlockName",  bpy.data, "texts", text = "")

    def drawAdvanced(self, layout):
        col = layout.column(align = True)
        for i, socket in enumerate(self.inputs[:-1]):
            col.prop(socket, '["dataWidth"]', text = "Width " + str(i + 1))

    @property
    def inputVariables(self):
        return {socket.identifier : "data_" + str(i) for i, socket in enumerate(self.inputs)}

    def getExecutionCode(self):
        names = ["data_" + str(i) for i in range(len(self.inputs[:-1]))]
        return "self.writeDebugData([{}])".format(", ".join(names))

    def writeDebugData(self, dataList):
        textBlock = self.textBlock
        if textBlock is None: return

        texts = []
        for data, socket in zip(dataList, self.inputs):
            if isinstance(data, float): text = str(round(data, 5))
            else: text = str(data)
            texts.append(text.rjust(socket["dataWidth"]))

        textBlock.write(" ".join(texts))
        textBlock.write("\n")

    @property
    def textBlock(self):
        return bpy.data.texts.get(self.textBlockName)

def clearDebugLoopTextBlocks(nodeTree):
    for node in getNodesByType("an_DebugLoopNode"):
        textBlock = node.textBlock
        if textBlock: textBlock.clear()
