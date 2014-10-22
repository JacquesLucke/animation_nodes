import math

def linear(x):
	return x
	
def expoEaseOut(x):
	return 1 - math.pow(2, -10*x)
def expoEaseIn(x):
	return math.pow(2, 10*(x-1))
def quadEaseOut(x):
	return -1 * x * (x-2)

def cubicEaseOut(x):
	x -= 1
	return x*x*x + 1
def cubicEaseIn(x):
	return x*x*x
def cubicEaseInOut(x):
	x *= 2
	if x < 1:
		return x*x*x / 2
	x -= 2
	return x*x*x / 2 + 1