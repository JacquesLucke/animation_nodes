cimport cython
from . color cimport Color
from . number cimport lerpFloat

cdef void addColor(Color* target, Color* a, Color* b):
    target.r = a.r + b.r
    target.g = a.g + b.g
    target.b = a.b + b.b
    target.a = a.a + b.a

cdef void addColor_Inplace(Color* c, Color* a):
    c.r += a.r
    c.g += a.g
    c.b += a.b
    c.a += a.a

cdef void scaleColor_Inplace(Color* c, float factor):
    c.r *= factor
    c.g *= factor
    c.b *= factor
    c.a *= factor

cdef void mixColor(Color* target, Color* x, Color* y, float factor):
    target.r = lerpFloat(x.r, y.r, factor)
    target.g = lerpFloat(x.g, y.g, factor)
    target.b = lerpFloat(x.b, y.b, factor)
    target.a = lerpFloat(x.a, y.a, factor)

# https://www.w3.org/TR/css-color-3/#hsl-color

cdef void hsla_to_rgba(Color* c, float h, float s, float l, float a):
    cdef float m1, m2

    if l <= 0.5: m2 = l * (s + 1)
    else: m2 = l + s - l * s

    m1 = l * 2 - m2
    c.r = hue_to_rgb(m1, m2, h + 1 / 3)
    c.g = hue_to_rgb(m1, m2, h)
    c.b = hue_to_rgb(m1, m2, h - 1 / 3)
    c.a = a

cdef float hue_to_rgb(float m1, float m2, float h):
    if h < 0: h += 1
    elif h > 1: h -= 1
    if h * 6 < 1: return m1 + (m2 - m1) * h * 6
    if h * 2 < 1: return m2
    if h * 3 < 2: return m1 + (m2 - m1) * (2 / 3 - h) * 6
    return m1

# https://en.wikipedia.org/wiki/HSL_and_HSV#Formal_derivation

@cython.cdivision(True)
cdef void rgba_to_hsla(Color* c, double* h, double* s, double* l, double* a):
    cdef float M = max(c.r, c.g, c.b)
    cdef float m = min(c.r, c.g, c.b)
    cdef float C = M - m

    if M == m:
        h[0] = 0
    elif M == c.r:
        h[0] = (c.g - c.b) / C
        if h[0] < 0:
            h[0] += 6
    elif M == c.g:
        h[0] = ((c.b - c.r) / C) + 2
    elif M == c.b:
        h[0] = ((c.r - c.g) / C) + 4
    h[0] /= 6

    l[0] = (M + m) / 2

    if l[0] == 0 or l[0] == 1:
        s[0] = 0
    else:
        s[0] = C / (1 - abs(2 * l[0] - 1))

    a[0] = c.a

# https://commons.wikimedia.org/wiki/File:HSV-RGB-comparison.svg

@cython.cdivision(True)
cdef void hsva_to_rgba(Color* c, float h, float s, float v, float a):
    cdef float i, f, w

    i = h * 6
    f = i % 1
    w = v * (1 - s)
    if i < 1:
        c.r = v
        c.g = w * (1 - f) + v * f
        c.b = w
    elif i < 2:
        c.r = w * f + v * (1 - f)
        c.g = v
        c.b = w
    elif i < 3:
        c.r = w
        c.g = v
        c.b = w * (1 - f) + v * f
    elif i < 4:
        c.r = w
        c.g = w * f + v * (1 - f)
        c.b = v
    elif i < 5:
        c.r = w * (1 - f) + v * f
        c.g = w
        c.b = v
    else:
        c.r = v
        c.g = w
        c.b = w * f + v * (1 - f)
    c.a = a

# https://en.wikipedia.org/wiki/HSL_and_HSV#Formal_derivation

@cython.cdivision(True)
cdef void rgba_to_hsva(Color* c, double* h, double* s, double* v, double* a):
    cdef float M = max(c.r, c.g, c.b)
    cdef float m = min(c.r, c.g, c.b)
    cdef float C = M - m

    if M == m:
        h[0] = 0
    elif M == c.r:
        h[0] = (c.g - c.b) / C
        if h[0] < 0:
            h[0] += 6
    elif M == c.g:
        h[0] = ((c.b - c.r) / C) + 2
    elif M == c.b:
        h[0] = ((c.r - c.g) / C) + 4
    h[0] /= 6

    v[0] = M

    if v[0] == 0:
        s[0] = 0
    else:
        s[0] = C / v[0]

    a[0] = c.a

# https://en.wikipedia.org/wiki/YIQ#FCC_NTSC_Standard

cdef void yiqa_to_rgba(Color* c, float y, float i, float q, float a):
    c.r = y + 0.9469 * i + 0.6236 * q
    c.g = y - 0.2748 * i - 0.6357 * q
    c.b = y - 1.1 * i + 1.7 * q
    c.a = a

# https://en.wikipedia.org/wiki/YIQ#FCC_NTSC_Standard

cdef void rgba_to_yiqa(Color* c, double* y, double* i, double* q, double* a):
    y[0] = 0.3 * c.r + 0.59 * c.g + 0.11 * c.b
    i[0] = 0.599 * c.r - 0.2773 * c.g - 0.3217 * c.b
    q[0] = 0.213 * c.r - 0.5251 * c.g + 0.3121 * c.b
    a[0] = c.a
