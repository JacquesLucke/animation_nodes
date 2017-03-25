from bpy.props import *
from collections import defaultdict
from . base_node import AnimationNode
from ... sockets.info import toListDataType
from .. effects import AutoSelectVectorization, VectorizeCodeEffect

codeEffectByIdentifier = {}

class VectorizedNode(AnimationNode):
    autoVectorizeExecution = False

    def create(self):
        self.vectorization = AutoSelectVectorization()
        self._reinitializeCodeEffect()
        self.createVectorized()
        self.newSocketEffect(self.vectorization)

    @classmethod
    def newVectorizeProperty(cls):
        return BoolProperty(default = False, update = AnimationNode.refresh)

    def newVectorizedInput(self, dataType, properties, baseData, listData):
        properties = self._formatInputProperties(properties)

        baseDataType = dataType
        listDataType = toListDataType(dataType)

        isCurrentlyList = getattr(self, properties[0])
        socket = self.newInputGroup(isCurrentlyList,
            [baseDataType] + list(baseData),
            [listDataType] + list(listData))

        self.vectorization.input(self, properties[0], socket, properties[1])
        if isCurrentlyList:
            self._codeEffect.input(baseData[1], listData[1])

    def newVectorizedOutput(self, dataType, properties, baseData, listData):
        properties = self._formatOutputProperties(properties)

        baseDataType = dataType
        listDataType = toListDataType(dataType)

        isCurrentlyList = self._evaluateOutputProperties(properties)
        socket = self.newOutputGroup(isCurrentlyList,
            [baseDataType] + list(baseData),
            [listDataType] + list(listData))

        self.vectorization.output(self, properties, socket)
        if isCurrentlyList:
            self._codeEffect.output(baseData[1], listData[1])

    def _formatInputProperties(self, properties):
        if isinstance(properties, str):
            return (properties, [])
        return properties

    def _formatOutputProperties(self, properties):
        if isinstance(properties, str):
            return [(properties, )]
        return properties

    def _evaluateInputProperties(self, properties):
        if not getattr(self, properties[0]):
            return False
        for group in properties[1]:
            if isinstance(group, str):
                if not getattr(self, group):
                    return False
            else:
                if not any(getattr(self, prop) for prop in group):
                    return False
        return True

    def _evaluateOutputProperties(self, properties):
        for group in properties:
            if isinstance(group, str):
                if not getattr(self, group):
                    return False
            else:
                if not any(getattr(self, prop) for prop in group):
                    return False
        return True

    def getCodeEffects(self):
        if not self.autoVectorizeExecution:
            return []
        return [self._codeEffect]

    def _reinitializeCodeEffect(self):
        self._clearCodeEffect()
        codeEffectByIdentifier[self.identifier] = VectorizeCodeEffect()

    def _clearCodeEffect(self):
        if self.identifier in codeEffectByIdentifier:
            del codeEffectByIdentifier[self.identifier]

    @property
    def _codeEffect(self):
        return codeEffectByIdentifier[self.identifier]
