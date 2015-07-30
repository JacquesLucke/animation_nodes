import bpy
from ... base_types.node import AnimationNode
from ... events import propertyChanged
from ... nodes.mn_node_helper import getHelperMaterial, getNotUsedMaterialNodeName
from ... algorithms.interpolation import *

topCategoryItems = [("LINEAR", "Linear", ""),
                    ("EXPONENTIAL", "Exponential", ""),
                    ("CUBIC", "Cubic", ""),
                    ("BACK", "Back", ""),
                    ("CUSTOM", "Custom", "")]
                    
exponentialCategoryItems = [("IN", "In", ""),
                            ("OUT", "Out", "")]
                            
cubicCategoryItems = [("IN", "In", ""),
                    ("OUT", "Out", ""),
                    ("INOUT", "In / Out", "")]
                    
backCategoryItems = [("IN", "In", ""),
                    ("OUT", "Out", "")]

class InterpolationNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_InterpolationNode"
    bl_label = "Interpolation"
    isDetermined = True
    
    inputNames =  { "Back" : "back" }
    outputNames = { "Interpolation" : "interpolation" }
    
    def topCategoryChanged(self, context):
        self.hideInputSockets()
        if self.topCategory == "BACK": self.inputs["Back"].hide = False
        propertyChanged()
    
    topCategory = bpy.props.EnumProperty(items = topCategoryItems, default = "LINEAR", update = topCategoryChanged, name = "Category")
    backCategory = bpy.props.EnumProperty(items = backCategoryItems, default = "OUT", update = propertyChanged, name = "Back")
    exponentialCategory = bpy.props.EnumProperty(items = exponentialCategoryItems, default = "OUT", update = propertyChanged, name = "Exponential")
    cubicCategory = bpy.props.EnumProperty(items = cubicCategoryItems, default = "OUT", update = propertyChanged, name = "Cubic")
    
    curveNodeName = bpy.props.StringProperty(default = "")
    
    def create(self):
        self.inputs.new("mn_FloatSocket", "Back").value = 1.70158
        self.outputs.new("mn_InterpolationSocket", "Interpolation")
        self.hideInputSockets()
        self.createCurveNode()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "topCategory", text = "")
        if self.topCategory == "BACK": layout.prop(self, "backCategory", text = "")
        if self.topCategory == "EXPONENTIAL": layout.prop(self, "exponentialCategory", text = "")
        if self.topCategory == "CUBIC": layout.prop(self, "cubicCategory", text = "")
        if self.topCategory == "CUSTOM":
            node = self.getCurveNode()
            layout.template_curve_mapping(node, "mapping", type = "NONE")
            self.callFunctionFromUI(layout, "resetCurveEndPoints", text = "Reset End Points")
        
    def execute(self, back):
        if self.topCategory == "LINEAR": return (linear, None)
        elif self.topCategory == "EXPONENTIAL":
            if self.exponentialCategory == "IN": return (expoEaseIn, None)
            elif self.exponentialCategory == "OUT": return (expoEaseOut, None)
        elif self.topCategory == "CUBIC":
            if self.cubicCategory == "IN": return (cubicEaseIn, None)
            elif self.cubicCategory == "OUT": return (cubicEaseOut, None)
            elif self.cubicCategory == "INOUT": return (cubicEaseInOut, None)
        elif self.topCategory == "BACK":
            if self.backCategory == "IN": return (backEaseIn, back)
            elif self.backCategory == "OUT": return (backEaseOut, back)
        elif self.topCategory == "CUSTOM":
            mapping = self.getMapping()
            return (curveInterpolation, (mapping.curves[3], mapping))
        return (linear, None)
        
    def hideInputSockets(self):
        for socket in self.inputs:
            socket.hide = True
            
    def duplicate(self, sourceNode):
        self.createCurveNode()
        curvePoints = self.getCurve().points
        for i, point in enumerate(sourceNode.getCurve().points):
            if len(curvePoints) == i:
                curvePoints.new(50, 50) #random start position
            curvePoints[i].location = point.location
            
    def delete(self):
        self.removeCurveNode()
        
    def getCurveNode(self):
        material = getHelperMaterial()
        nodeTree = material.node_tree
        node = nodeTree.nodes.get(self.curveNodeName)
        if node is None:
            self.createCurveNode()
        return node
    def getMapping(self):
        return self.getCurveNode().mapping
    def getCurve(self):
        return self.getMapping().curves[3]
        
    def createCurveNode(self):
        self.curveNodeName = getNotUsedMaterialNodeName()
        material = getHelperMaterial()
        nodeTree = material.node_tree
        node = nodeTree.nodes.new("ShaderNodeRGBCurve")
        node.name = self.curveNodeName
        self.resetCurveEndPoints()
    def removeCurveNode(self):
        nodeTree = getHelperMaterial().node_tree
        node = nodeTree.nodes.get(self.curveNodeName)
        if node is not None:
            nodeTree.nodes.remove(node)
        self.curveNodeName = ""
        
    
    def resetCurveEndPoints(self):
        curvePoints = self.getCurve().points
        curvePoints[0].location = [0, 0.25]
        curvePoints[-1].location = [1, 0.75]