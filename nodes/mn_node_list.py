def getNodeNameDictionary():
	nodes = []
	
	nodes.append(("Input", [
		"mn_IntegerInputNode",
		"mn_FloatInputNode",
		"mn_StringInputNode",
		"mn_ObjectInputNode",
		"mn_TimeInfoNode",
		"mn_ObjectInfoNode",
		"mn_RandomNumberNode",
		"mn_RandomStringNode",
		"mn_CharactersNode",
		"mn_FloatListInputNode",
		"mn_StringListInputNode",
		"mn_ObjectListInputNode",
		"mn_SoundBakeNode",
		"mn_SoundInputNode",
		"mn_ColorInputNode" ] ))
		
	nodes.append(("Generate", [
		"mn_ReplicateObjectNode" ] ))
		
	nodes.append(("Output", [
		"mn_TextOutputNode",
		"mn_ObjectOutputNode",
		"mn_AttributeOutputNode",
		"mn_DebugOutputNode",
		"mn_ModifierOutputNode",
		"mn_CopyTransformsNode",
		"mn_MaterialOutputNode" ] ))
		
	nodes.append(("Strings", [
		"mn_CombineStringsNode",
		"mn_ReplicateStringsNode",
		"mn_SubstringNode",
		"mn_StringAnalyzeNode" ] ))

	nodes.append(("Convert", [
		"mn_ToStringConversion",
		"mn_ToFloatConversion",
		"mn_ToIntegerConversion",
		"mn_CombineVector",
		"mn_SeparateVector" ] ))
	
	nodes.append(("Math", [
		"mn_FloatMathNode",
		"mn_VectorLengthNode" ] ))
		
	nodes.append(("List", [
		"mn_GetListElementNode",
		"mn_GetListLengthNode",
		"mn_SetListElementNode",
		"mn_SumListElementsNode",
		"mn_CombineListsNode",
		"mn_ShuffleListNode" ] ))
		
	nodes.append(("Script", [
		"ExpressionNode" ] ))
		
	nodes.append(("System", [
		"SubProgramNode",
		"SubProgramStartNode",
		"EnumerateObjectsStartNode",
		"EnumerateObjectsNode" ] ))
	return nodes