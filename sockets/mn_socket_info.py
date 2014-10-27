listChains = [
	["mn_FloatSocket", "mn_FloatListSocket"],
	["mn_ObjectSocket", "mn_ObjectListSocket"],
	["mn_StringSocket", "mn_StringListSocket"] ]
	
def getListSocketType(socketType):
	for listChain in listChains:
		if socketType in listChain:
			index = listChain.index(socketType)
			if index == len(listChain) - 1: return None
			return listChain[index + 1]
	return None
	