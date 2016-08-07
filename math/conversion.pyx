cdef void toMatrix4(Matrix4* m, value):
    m.a11 = value[0][0]
    m.a12 = value[0][1]
    m.a13 = value[0][2]
    m.a14 = value[0][3]

    m.a21 = value[1][0]
    m.a22 = value[1][1]
    m.a23 = value[1][2]
    m.a24 = value[1][3]

    m.a31 = value[2][0]
    m.a32 = value[2][1]
    m.a33 = value[2][2]
    m.a34 = value[2][3]

    m.a41 = value[3][0]
    m.a42 = value[3][1]
    m.a43 = value[3][2]
    m.a44 = value[3][3]
