import numpy as np
import math


# Transforms vector into unit vector with same direction
def unit_vector(vector):
    return vector / math.sqrt(vector[0] ** 2 + vector[1] ** 2)


# Computes angle between two vectors
def min_angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def clockwise_angle_between(v1, v2):
    inner_angle = min_angle_between(v1, v2)

    # computes the determinant (vectorial product) between the two vectors to
    # decide if the angle is in [0,pi] or in (pi,2pi) 
    det = v1[0] * v2[1] - v1[1] * v2[0]
    if det >= 0.0:
        alpha = inner_angle
    else:
        alpha = 2 * np.pi - inner_angle

    return alpha


# Computes angle between vector and X axis
def angle(v1):
    v1_u = unit_vector(v1)
    v2_u = [1.0, 0.0]
    alpha = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    # if vector is on negative Y coordinate, invert sign  
    if v1_u[1] < 0.0:
        alpha += np.pi / 2

    return alpha


# Verify if edges are the same
def equal_edges(e1, e2):
    if (e1[0] == e2[0]) and (e1[1] == e2[1]):
        return True
    if (e1[1] == e2[0]) and (e1[0] == e2[1]):
        return True

    return False


# Computes distance between two points
def distance_between(v1, v2):
    difference_vector = v2 - v1
    return math.sqrt(difference_vector[0] ** 2 + difference_vector[1] ** 2)
