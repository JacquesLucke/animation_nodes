def getNodeNameDictionary():
	nodes = []
	
	nodes.append(("Input", [
		"IntegerInputNode",
		"FloatInputNode",
		"StringInputNode",
		"ObjectInputNode",
		"TimeInfoNode",
		"ObjectInfoNode",
		"RandomNumberNode",
		"RandomStringNode",
		"CharactersNode",
		"FloatListInputNode",
		"StringListInputNode",
		"ObjectListInputNode",
		"SoundInputNode" ] ))
		
	nodes.append(("Generate", [
		"ReplicateObjectNode" ] ))
		
	nodes.append(("Output", [
		"TextOutputNode",
		"ObjectOutputNode",
		"AttributeOutputNode",
		"DebugOutputNode",
		"ModifierOutputNode",
		"CopyTransformsNode",
		"MaterialOutputNode" ] ))
		
	nodes.append(("Strings", [
		"CombineStringsNode",
		"ReplicateStringsNode",
		"SubstringNode",
		"StringAnalyzeNode" ] ))

	nodes.append(("Convert", [
		"ToStringConversion",
		"ToFloatConversion",
		"ToIntegerConversion",
		"CombineVector",
		"SeparateVector" ] ))
	
	nodes.append(("Math", [
		"FloatMathNode",
		"VectorLengthNode" ] ))
		
	nodes.append(("List", [
		"GetListElementNode",
		"GetListLengthNode",
		"SetListElementNode",
		"SumListElementsNode",
		"CombineListsNode",
		"ShuffleListNode" ] ))
		
	nodes.append(("Script", [
		"ExpressionNode" ] ))
		
	nodes.append(("System", [
		"SubProgramNode",
		"SubProgramStartNode",
		"EnumerateObjectsStartNode",
		"EnumerateObjectsNode" ] ))
	return nodes