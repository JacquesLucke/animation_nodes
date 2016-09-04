import bpy
from ... base_types import Template

class FCurveAnimationOffsetTemplate(bpy.types.Operator, Template):
    bl_idname = "an.fcurve_animation_offset_template"
    bl_label = "FCurve Animation Offset"
    nodeOffset = (-500, 200)

    def insert(self):

        # Nodes
        ####################################################################

        # Main Unit
        sourceObjectNode = self.newNode("an_DataInputNode", x = 0, y = 0, label = "Source Object")
        sourceObjectNode.assignedType = "Object"

        timeInfoNode = self.newNode("an_TimeInfoNode", x = 0, y = -200)
        additionalOffsetNode = self.newNode("an_TranslationMatrixNode", x = 0, y = -325)
        additionalOffsetNode.inputs[0].value = [4, 3, 0]
        individualOffsetNode = self.newNode("an_ComposeMatrixNode", x = 220, y = -325)
        individualOffsetNode.inputs[0].value = [3, 0, 0]
        delayTimeNode = self.newNode("an_DelayTimeNode", x = 220, y = -200)
        objectInstancer = self.newNode("an_ObjectInstancerNode", x = 220, y = 150)
        objectInstancer.copyObjectProperties = True
        objectInstancer.removeAnimationData = True
        objectInstancer.inputs[0].value = 5
        invokeAnimationOffsetNode = self.newNode("an_InvokeSubprogramNode", x = 500, y = -80)

        # Animation Offset Group

        animationOffsetGroupInputNode = self.newNode("an_GroupInputNode", x = 0, y = -845)
        animationOffsetGroupInputNode.subprogramName = "FCurve Animation Offset"
        animationOffsetGroupInputNode.newParameter("Object", name = "Source")
        animationOffsetGroupInputNode.newParameter("Object List", name = "Targets")
        animationOffsetGroupInputNode.newParameter("Float", name = "Frame")
        animationOffsetGroupInputNode.newParameter("Float", name = "Time Offset").value = 10
        animationOffsetGroupInputNode.newParameter("Matrix", name = "Additional Offset")
        animationOffsetGroupInputNode.newParameter("Matrix", name = "Individual Offset")

        fCurvesFromObjectNode = self.newNode("an_FCurvesFromObjectNode", x = 250, y = -775)
        invokeObjectLoopNode = self.newNode("an_InvokeSubprogramNode", x = 470, y = -745)

        animationOffsetGroupOutputNode = self.newNode("an_GroupOutputNode", x = 700, y = -745)
        animationOffsetGroupOutputNode.newReturn("Object List", name = "Targets")

        # Object Loop

        objectLoopInputNode = self.newNode("an_LoopInputNode", x = 0, y = -1300)
        objectLoopInputNode.subprogramName = "Object Loop"
        objectLoopInputNode.newIterator("Object List", name = "Target").loop.useAsOutput = True
        objectLoopInputNode.newParameter("Object", name = "Source")
        objectLoopInputNode.newParameter("FCurve List", name = "FCurve List")
        objectLoopInputNode.newParameter("Float", name = "Frame")
        objectLoopInputNode.newParameter("Float", name = "Time Offset")
        objectLoopInputNode.newParameter("Matrix", name = "Additional Offset")
        objectLoopInputNode.newParameter("Matrix", name = "Individual Offset")
        accumulatedTransformationSocket = objectLoopInputNode.newParameter("Matrix", name = "Accumulated Transformation")
        accumulatedTransformationSocket.loop.useAsInput = False

        multiplyIndexAndOffsetNode = self.newNode("an_FloatMathNode", x = 350, y = -1200)
        subtractOffsetFromFrameNode = self.newNode("an_FloatMathNode", x = 550, y = -1200)
        subtractOffsetFromFrameNode.operation = "SUBTRACT"
        calculateAccumulatedMatrixNode = self.newNode("an_MatrixMathNode", x = 350, y = -1580)
        reassignAccumulatedMatrixNode = self.newNode("an_ReassignLoopParameterNode", x = 540, y = -1580)
        copyTransformsNode = self.newNode("an_CopyTransformsNode", x = 550, y = -1340)
        copyTransformsNode.width = 140
        invokeCopyFCurvesNode = self.newNode("an_InvokeSubprogramNode", x = 760, y = -1200)
        updateMatrixNode = self.newNode("an_UpdateObjectMatricesNode", x = 1030, y = -1330)
        localTransformNode = self.newNode("an_TransformObjectNode", x = 1230, y = -1370)
        localTransformNode.useCenter = True
        additionalTransformNode = self.newNode("an_TransformObjectNode", x = 1450, y = -1415)
        additionalTransformNode.useCenter = False

        # Copy FCurves Loop

        copyFCurvesLoopInput = self.newNode("an_LoopInputNode", x = 0, y = -1850)
        copyFCurvesLoopInput.subprogramName = "Copy FCurves"
        copyFCurvesLoopInput.newIterator("FCurve List", name = "FCurve")
        copyFCurvesLoopInput.newParameter("Object", name = "Object").loop.useAsOutput = True
        copyFCurvesLoopInput.newParameter("Float", name = "Frame Offset")

        fCurveInfoNode = self.newNode("an_FCurveInfoNode", x = 300, y = -1850)
        evaluateFCurveNode = self.newNode("an_EvaluateFCurveNode", x = 300, y = -2000)
        evaluateFCurveNode.frameType = "ABSOLUTE"
        objectDataPathOutputNode = self.newNode("an_ObjectDataPathOutputNode", x = 550, y = -1910)

        self.updateSubprograms()

        invokeAnimationOffsetNode.subprogramIdentifier = animationOffsetGroupInputNode.identifier
        animationOffsetGroupOutputNode.groupInputIdentifier = animationOffsetGroupInputNode.identifier
        invokeObjectLoopNode.subprogramIdentifier = objectLoopInputNode.identifier
        reassignAccumulatedMatrixNode.loopInputIdentifier = objectLoopInputNode.identifier
        reassignAccumulatedMatrixNode.parameterIdentifier = accumulatedTransformationSocket.identifier
        invokeCopyFCurvesNode.subprogramIdentifier = copyFCurvesLoopInput.identifier

        self.updateSubprograms()


        # Links
        ####################################################################

        # Main Unit

        self.newLink(sourceObjectNode.outputs[0], objectInstancer.inputs[1])
        self.newLink(timeInfoNode.outputs[0], delayTimeNode.inputs[0])
        self.newLink(sourceObjectNode.outputs[0], invokeAnimationOffsetNode.inputs[0])
        self.newLink(objectInstancer.outputs[0], invokeAnimationOffsetNode.inputs[1])
        self.newLink(delayTimeNode.outputs[0], invokeAnimationOffsetNode.inputs[2])
        self.newLink(additionalOffsetNode.outputs[0], invokeAnimationOffsetNode.inputs[4])
        self.newLink(individualOffsetNode.outputs[0], invokeAnimationOffsetNode.inputs[5])

        # Animation Offset Group

        self.newLink(animationOffsetGroupInputNode.outputs[0], fCurvesFromObjectNode.inputs[0])
        self.newLink(animationOffsetGroupInputNode.outputs[0], invokeObjectLoopNode.inputs[1])
        self.newLink(animationOffsetGroupInputNode.outputs[1], invokeObjectLoopNode.inputs[0])
        self.newLink(animationOffsetGroupInputNode.outputs[2], invokeObjectLoopNode.inputs[3])
        self.newLink(animationOffsetGroupInputNode.outputs[3], invokeObjectLoopNode.inputs[4])
        self.newLink(animationOffsetGroupInputNode.outputs[4], invokeObjectLoopNode.inputs[5])
        self.newLink(animationOffsetGroupInputNode.outputs[5], invokeObjectLoopNode.inputs[6])
        self.newLink(fCurvesFromObjectNode.outputs[0], invokeObjectLoopNode.inputs[2])
        self.newLink(invokeObjectLoopNode.outputs[0], animationOffsetGroupOutputNode.inputs[0])

        # Object Loop

        self.newLink(objectLoopInputNode.outputs[0], multiplyIndexAndOffsetNode.inputs[0])
        self.newLink(objectLoopInputNode.outputs[2], copyTransformsNode.inputs[1])
        self.newLink(objectLoopInputNode.outputs[4], copyTransformsNode.inputs[0])
        self.newLink(objectLoopInputNode.outputs[5], invokeCopyFCurvesNode.inputs[0])
        self.newLink(objectLoopInputNode.outputs[6], subtractOffsetFromFrameNode.inputs[0])
        self.newLink(objectLoopInputNode.outputs[7], multiplyIndexAndOffsetNode.inputs[1])
        self.newLink(objectLoopInputNode.outputs[8], additionalTransformNode.inputs[1])
        self.newLink(objectLoopInputNode.outputs[9], calculateAccumulatedMatrixNode.inputs[0])
        self.newLink(objectLoopInputNode.outputs[10], calculateAccumulatedMatrixNode.inputs[1])
        self.newLink(objectLoopInputNode.outputs[10], localTransformNode.inputs[1])
        self.newLink(multiplyIndexAndOffsetNode.outputs[0], subtractOffsetFromFrameNode.inputs[1])
        self.newLink(subtractOffsetFromFrameNode.outputs[0], invokeCopyFCurvesNode.inputs[2])
        self.newLink(calculateAccumulatedMatrixNode.outputs[0], reassignAccumulatedMatrixNode.inputs[0])
        self.newLink(copyTransformsNode.outputs[0], invokeCopyFCurvesNode.inputs[1])
        self.newLink(invokeCopyFCurvesNode.outputs[0], updateMatrixNode.inputs[0])
        self.newLink(updateMatrixNode.outputs[0], localTransformNode.inputs[0])
        self.newLink(localTransformNode.outputs[0], additionalTransformNode.inputs[0])

        # Copy FCurves Loop

        self.newLink(copyFCurvesLoopInput.outputs[2], evaluateFCurveNode.inputs[0])
        self.newLink(copyFCurvesLoopInput.outputs[2], fCurveInfoNode.inputs[0])
        self.newLink(copyFCurvesLoopInput.outputs[4], objectDataPathOutputNode.inputs[0])
        self.newLink(copyFCurvesLoopInput.outputs[5], evaluateFCurveNode.inputs[1])
        self.newLink(fCurveInfoNode.outputs[0], objectDataPathOutputNode.inputs[1])
        self.newLink(fCurveInfoNode.outputs[1], objectDataPathOutputNode.inputs[2])
        self.newLink(evaluateFCurveNode.outputs[0], objectDataPathOutputNode.inputs[3])
