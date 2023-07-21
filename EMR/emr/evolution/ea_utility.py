import math
import random

def mutate_value(v, mutation_rate, mutation_sigma, clamp = True):
    if (random.uniform(0,1) < mutation_rate):
        v = random.gauss(v,mutation_sigma)
    if clamp == True:
        v = max(min(v, 1.0), -1.0)
    return v