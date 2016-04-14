class Struct:
    def __init__(self):
        self.data = {}

    def copy(self):
        return self

    def __repr__(self):
        return "<AN Struct: {} >".format(self.data)
