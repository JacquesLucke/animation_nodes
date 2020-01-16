class Vector2D:
    def __init__(self, vector):
        if len(vector) != 2:
            raise ValueError("Expected a tuple of 2 numbers.")
        self.vector = list(vector)

    def __len__(self):
        return 2

    def __getitem__(self, key):
        return self.vector[key]
    
    def __repr__(self):
        return f"Vector2D(X: {self.x:.2f}, Y: {self.y:.2f})"

    def copy(self):
      return Vector2D(self.vector)

    @property
    def x(self):
        return self.vector[0]

    @property
    def y(self):
        return self.vector[1]

    @x.setter
    def x(self, x):
        self.vector[0] = x

    @y.setter
    def y(self, y):
        self.vector[1] = y

