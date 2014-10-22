import math

def linear(x):
	return x
	
def expoEaseOut(x):
	return 1 - math.pow(2, -10*x)
def expoEaseIn(x):
	return math.pow(2, 10*(x-1))