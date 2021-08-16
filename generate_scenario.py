import click
import math
import json
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
from scenario import Scenario, distance_between

FIXED=1
NOT_FIXED=0

SPRING=0
ROPE=2

hinge_point = [1.0, 0.0]

def get_end_point(length, theta):
    x = math.cos(theta) * length
    y = math.sin(theta) * length
    
    return [hinge_point[0] + x, y]

def point_between(start, end, total, index):
    percentage = float(index) / total

    #print(end[0]-start[0], percentage)
    return [start[0] + (end[0] - start[0]) * percentage, start[1] + (end[1] - start[1]) * percentage]

@click.command()
@click.option('--open-angle', help='Full open angle', type=float, prompt=True)
@click.option('--rest-angle', help='Rest angle', type=float, prompt=True)
@click.option('--length', help='Length of watergate', type=float, prompt=True)
@click.option('--vertices', help='Number of vertices per edge', type=int, prompt=True)
@click.option('--boyant-radius', help='Boyant radius of each vertex', default=0.05, type=float)
@click.option('--ropes', help='Number of ropes', type=int, prompt=True)
@click.option('--water-level', help='Starting water level', default=1.0, type=float)
@click.option('--open-in-browser', is_flag=True)
@click.argument('filename')
def generate_scenario(open_angle, rest_angle, length, vertices, boyant_radius, ropes, water_level, open_in_browser, filename):
    scenario = Scenario(water_level)

    scenario.add_vertex(hinge_point, FIXED, 0.0)

    end_floor = [hinge_point[0] + length, 0.0]
    end_gate = get_end_point(length, math.radians(rest_angle))

    # build floor vertices
    last_vertex = 0
    for n in range(1, vertices + 1):
        new_point = point_between(hinge_point, end_floor, vertices, n)
        scenario.add_vertex(new_point, FIXED, 0.0)
        second_vertex = len(scenario.vertices) - 1
        scenario.add_edge([last_vertex, second_vertex], SPRING)
        last_vertex = second_vertex
    
    # build gate vertices
    last_vertex = 0
    for n in range(1, vertices + 1):
        new_point = point_between(hinge_point, end_gate, vertices, n)
        scenario.add_vertex(new_point, NOT_FIXED, boyant_radius)
        second_vertex = len(scenario.vertices) - 1
        scenario.add_edge([last_vertex, second_vertex], SPRING)
        last_vertex = second_vertex

    end_gate_open = get_end_point(length, math.radians(open_angle))
    remove_every_rope = None
    if ropes is not None:
        remove_every_rope = math.ceil(float(vertices) / ropes)

    # add ropes
    for n in range(1, vertices + 1):
        if remove_every_rope is None or n % remove_every_rope == 0:
            ground_point = point_between(hinge_point, end_floor, vertices, n)
            open_point = point_between(hinge_point, end_gate_open, vertices, n)
            edge_length = distance_between(ground_point, open_point)
            ground_vertex = n
            gate_vertex = vertices + n
            scenario.add_edge([ground_vertex, gate_vertex], ROPE, edge_length)

    result = scenario.to_json()
    with open('./scenarios/' + filename, 'w') as outfile:
        json.dump(result, outfile)

    if open_in_browser:
        os.system('open http://localhost:5000?scenario=' + filename)

if __name__ == '__main__':
    generate_scenario()
