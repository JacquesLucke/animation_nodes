from .. sockets.info import getCopyFunction

class Struct(dict):

    def copyValues(self):
        s = Struct()
        for (dataType, name), value in self.items():
            s[(dataType, name)] = getCopyFunction(dataType)(value)
        return s

    def __repr__(self):
        elements = [repr(name) + ": " + str(value) for (_, name), value in self.items()]
        return "<AN Struct: {} >".format(", ".join(elements))
