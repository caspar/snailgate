import math

# Computes distance between two points
# TODO: move elsewhere
def distance_between(v1, v2):
    difference_vector = [v2[0] - v1[0], v2[1] - v1[1]]
    return math.sqrt(difference_vector[0] ** 2 + difference_vector[1] ** 2)

def map_attribute(array, attribute):
    return list(map(lambda x: getattr(x, attribute), array))

class Vertex(object):
    def __init__(self, point, vertex_type, boyant_radius):
        self.point = point
        self.type = vertex_type
        self.boyant_radius = boyant_radius

class Edge(object):
    def __init__(self, vertices, edge_type, edge_length, edge_splits):
        self.vertices = vertices
        self.type = edge_type
        self.length = edge_length
        self.splits = edge_splits

class Scenario(object):
    def __init__(self, water_level):
        self.vertices = list()
        self.edges = list()
        self.water_level = water_level

    def add_vertex(self, point, vertex_type, boyant_radius):
        self.vertices.append(Vertex(point, vertex_type, boyant_radius))

    def add_edge(self, vertices, edge_type, edge_length = None, edge_splits = 0):
        if (edge_length is None):
            edge_length = distance_between(self.vertices[vertices[0]].point, self.vertices[vertices[1]].point)
        self.edges.append(Edge(vertices, edge_type, edge_length, edge_splits))

    def to_json(self):
        return { 
            'waterLevel': self.water_level,
            'vertices': map_attribute(self.vertices, 'point'),
            'vertexTypes': map_attribute(self.vertices, 'type'),
            'vertexBoyantRadiai': map_attribute(self.vertices, 'boyant_radius'),
            'edges': map_attribute(self.edges, 'vertices'),
            'edgeTypes': map_attribute(self.edges, 'type'),
            'edgeLengths': map_attribute(self.edges, 'length'),
            'edgeSplits': map_attribute(self.edges, 'splits')
        }
