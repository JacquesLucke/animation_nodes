import bpy
from ... base_types.node import AnimationNode
from ... sockets.info import *

class ConvertNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertNode"
    bl_label = "Convert"
    isDetermined = True

    inputNames = { "Old" : "old" }
    outputNames = { "New" : "new"}

    convertType = bpy.props.StringProperty(default = "Integer")

    def create(self):
        self.inputs.new("an_GenericSocket", "Old")
        self.buildOutputSocket()

    def edit(self):
        link = self.getFirstOutputLink()
        if link is not None:
            fromSocket = link.from_socket
            toSocket = link.to_socket
            if toSocket.node.type != "REROUTE":
                if fromSocket.dataType != toSocket.dataType:
                    self.convertType = toSocket.dataType
                    self.buildOutputSocket()

    def getFirstOutputLink(self):
        links = self.getLinksFromOutputSocket()
        if len(links) == 1: return links[0]
        return None

    def getLinksFromOutputSocket(self):
        socket = self.outputs.get("New")
        if socket is not None:
            return socket.links
        return []

    def buildOutputSocket(self):
        self.outputs.clear()
        self.outputs.new(toIdName(self.convertType), "New")

    def getInputSocketNames(self):
        return {"Old" : "old"}
    def getOutputSocketNames(self):
        return {"New" : "new"}

    def getExecutionCode(self):
        t = self.convertType
        if t == "Float": return ("try: $new$ = float(%old%) \n"
                                 "except: $new$ = 0")
        elif t == "Integer": return ("try: $new$ = int(%old%) \n"
                                     "except: $new$ = 0")
        elif t == "String": return ("try: $new$ = str(%old%) \n"
                                    "except: $new$ = ''")
        elif t == "Vector": return ("try: $new$ = mathutils.Vector(%old%) \n"
                                    "except: $new$ = mathutils.Vector((0, 0, 0))")
        else:
            return "$new$ = %old%"

    def getModuleList(self):
        t = self.convertType
        if t == "Vector": return ["mathutils"]
        return []
