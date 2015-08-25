import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class DebugNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DebugNode"
    bl_label = "Debug"

    printData = BoolProperty(default = False, name = "Print to Console")
    writeData = BoolProperty(default = False, name = "Write into Text Block")

    def create(self):
        self.newInput()

    def newInput(self):
        socket = self.inputs.new("an_GenericSocket", "Data", "data")
        socket.displayCustomName = True
        socket.customName = ""
        socket.removeable = True
        socket.moveable = True
        socket["dataWidth"] = 10

    def drawAdvanced(self, layout):
        self.invokeFunction(layout, "newInput", text = "New Input", icon = "PLUS")
        layout.prop(self, "printData")
        layout.prop(self, "writeData")

        col = layout.column(align = True)
        for i, socket in enumerate(self.inputs):
            col.prop(socket, '["dataWidth"]', text = "Width " + str(i + 1))

    @property
    def inputNames(self):
        return {socket.identifier : "data_" + str(i) for i, socket in enumerate(self.inputs)}

    def getExecutionCode(self):
        names = ["data_" + str(i) for i in range(len(self.inputs))]
        return "self.writeDebugData([{}])".format(", ".join(names))

    def writeDebugData(self, dataList):
        texts = []
        for data, socket in zip(dataList, self.inputs):
            if isinstance(data, float): text = str(round(data, 5))
            else: text = str(data)
            socket.customName = text
            texts.append(text.rjust(socket["dataWidth"]))
        if self.printData: print(" ".join(texts))
        if self.writeData:
            textBlock = getDebugTextBlock(self.nodeTree)
            textBlock.write(" ".join(texts))
            textBlock.write("\n")

def clearDebugTextBlock(nodeTree):
    getDebugTextBlock(nodeTree).clear()

def getDebugTextBlock(nodeTree):
    name = "Debug: " + repr(nodeTree.name)
    text = bpy.data.texts.get(name)
    if text is None:
        text = bpy.data.texts.new(name)
    return text
