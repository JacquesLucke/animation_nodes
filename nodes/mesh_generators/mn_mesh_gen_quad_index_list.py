import bpy
import mathutils
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

defaultNrSamples = 2

class mn_MeshGenerationQuadIndexList(Node, AnimationNode):
    bl_idname = "mn_MeshGenerationQuadIndexList"
    bl_label = "Quad Index List"

    closeU = bpy.props.BoolProperty(name = "Close U", default = False)
    closeV = bpy.props.BoolProperty(name = "Close V", default = False)
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "closeU")
        layout.prop(self, "closeV")

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Samples U").number = defaultNrSamples
        self.inputs.new("mn_IntegerSocket", "Samples V").number = defaultNrSamples
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Samples U" : "samplesU",
                "Samples V" : "samplesV"}

    def getOutputSocketNames(self):
        return {"Polygon Indices" : "polygonIndices"}

    def canExecute(self, samplesU, samplesV):
        if samplesU < 2: return False
        if samplesV < 2: return False
            
        return True

    def execute(self, samplesU, samplesV):
        polygonIndices = []
        if not self.canExecute(samplesU, samplesV):
            print("### NOT mn_MeshGenerationQuadIndexList.canExecute(samplesU, samplesV)")
            return polygonIndices
        
        try:
            for iU in range(samplesU - 1):
                currIU = iU * samplesV
                nextIU = currIU + samplesV
                for iV in range(samplesV - 1):
                    indexBL = currIU + iV
                    indexTL = indexBL + 1
                    indexBR = nextIU + iV
                    indexTR = indexBR + 1

                    polygonIndices.append([indexBL, indexBR, indexTR, indexTL])
                    
            if self.closeU: print("### TODO: mn_MeshGenerationQuadIndexList.closeU")
            if self.closeV: print("### TODO: mn_MeshGenerationQuadIndexList.closeV")
        except:
            print("### EXCEPT: mn_MeshGenerationQuadIndexList.execute(self, samplesU, samplesV)")
            return polygonIndices
        
        return polygonIndices
