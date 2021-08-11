import click
import json
import sys
import os
import math
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
from scenario import Scenario, distance_between

FIXED = 1
NOT_FIXED = 0

SPRING = 0
ROPE = 2

hinge_point = [2.0, 0.0]

def create_snailgate(base_left_index, base_right_index, bradius_intermediate, bradius_last, curvature_rope, curvature,
                     distance_leveling_buoy, edge_splits, leveling_buoy, long_rope_length, pieces, pieces_size,
                     scenario, vertical_folded_offset, spring_buoys_connection, leveling_buoy_ground_rope,
                     horizontal_rope, split_buoys, split_buoys_same_size, sign, layer):

    last_vertex = base_left_index
    end_floor = scenario.vertices[base_right_index].point

    if spring_buoys_connection:
        last_vertex = len(scenario.vertices)

        new_left_base_vertex = [end_floor[0] - distance_leveling_buoy, end_floor[1] + vertical_folded_offset]
        scenario.add_vertex(new_left_base_vertex, NOT_FIXED, bradius_intermediate)

        create_real_splits(scenario, base_right_index, last_vertex, edge_splits, bradius_intermediate)

    # build pieces
    for index in range(0, pieces):
        fold_percentage = curvature
        # each piece is composed of three segments o----x--x----o
        # initial and final segment have size 'a', while the middle one has size 'fold_percentage * a'.
        # To be able to store in rest position, first segment goes to the left, the second goes to the right and the
        # the third goes again to the right. The idea is that the rope should have size '(2 - fold_percentage) * a'
        a = pieces_size / (2 + fold_percentage)

        p1 = scenario.vertices[last_vertex].point
        p2 = [p1[0] + sign * a, vertical_folded_offset + p1[1]]
        p3 = [p2[0] - sign * a * fold_percentage, vertical_folded_offset + p2[1]]
        p4 = [p3[0] + sign * a, vertical_folded_offset + p3[1]]

        following_vertex = len(scenario.vertices)

        scenario.add_vertex(p2, NOT_FIXED, bradius_intermediate)
        scenario.add_vertex(p3, NOT_FIXED, bradius_intermediate)
        scenario.add_vertex(p4, NOT_FIXED, bradius_intermediate)

        create_real_splits(scenario, last_vertex, following_vertex, edge_splits, bradius_intermediate)
        create_real_splits(scenario, following_vertex, following_vertex + 1, edge_splits, bradius_intermediate)
        create_real_splits(scenario, following_vertex + 1, following_vertex + 2, edge_splits, bradius_intermediate)

        if curvature_rope:
            scenario.add_edge([last_vertex, following_vertex + 2], ROPE, (2 - fold_percentage) * a)

        last_vertex = following_vertex + 2

        sign *= -1

    scenario.vertices[last_vertex].boyant_radius = bradius_last
    if not long_rope_length is None:
        if split_buoys is None:
            scenario.add_edge([last_vertex, base_right_index], ROPE, long_rope_length)
        else:
            if not split_buoys_same_size:
                create_real_splits(scenario, last_vertex, base_right_index, split_buoys, bradius_last, ROPE, long_rope_length)
            else:
                num_fits = int(long_rope_length / (2 * bradius_last))
                create_real_splits(scenario, last_vertex, base_right_index, num_fits, bradius_last, ROPE, long_rope_length)

    if leveling_buoy:
        big_buoy = bradius_last
        leveling_buoy_index = len(scenario.vertices)
        if spring_buoys_connection:
            left_point = scenario.vertices[last_vertex].point
            scenario.add_vertex([left_point[0] + distance_leveling_buoy, left_point[1]], NOT_FIXED, big_buoy)
            create_real_splits(scenario, last_vertex, leveling_buoy_index, edge_splits, bradius_intermediate)
        else:
            scenario.add_vertex([end_floor[0] - (2 - fold_percentage) * a, big_buoy], NOT_FIXED, big_buoy)
            if horizontal_rope:
                scenario.add_edge([last_vertex, leveling_buoy_index], ROPE, distance_leveling_buoy)
        if not split_buoys_same_size:
            scenario.add_edge([base_right_index, leveling_buoy_index], ROPE, (2 - fold_percentage) * a)
        else:
            rope_length = (2 - fold_percentage) * a
            num_fits = int(rope_length / (2 * bradius_last))
            create_real_splits(scenario, base_right_index, leveling_buoy_index, num_fits, bradius_last, ROPE, rope_length)

        base_right_index = leveling_buoy_index

        if leveling_buoy_ground_rope:
            height = (2 - curvature) * a
            damping_factor = 1.0
            scenario.add_edge([1, leveling_buoy_index], ROPE, height * layer * damping_factor)

    base_left_index = last_vertex

    return base_left_index, base_right_index


def create_real_splits(scenario, initial_index, final_index, num_splits, bradius, type=SPRING, length=None):
    initial_node = np.array(scenario.vertices[initial_index].point)
    final_node = np.array(scenario.vertices[final_index].point)

    direction = (final_node - initial_node)
    unit_direction = direction / np.linalg.norm(direction)
    delta = np.linalg.norm(direction) / num_splits

    last_index = initial_index
    for index in range(1, num_splits):
        new_pos = initial_node + index * delta * unit_direction

        new_vertex_index = len(scenario.vertices)
        scenario.add_vertex(new_pos.tolist(), NOT_FIXED, bradius)

        if type == ROPE:
            scenario.add_edge([last_index, new_vertex_index], ROPE, length/num_splits)
        else:
            scenario.add_edge([last_index, new_vertex_index], SPRING)

        last_index = new_vertex_index

    if type == ROPE:
        scenario.add_edge([last_index, final_index], ROPE, length/num_splits)
    else:
        scenario.add_edge([last_index, final_index], SPRING)



@click.command()
@click.option('--number-snailgates', help='Number of stacked snailgates', type=int, default=1)
@click.option('--long-rope-length', help='Length of rope connecting beginning to end of snailgate', type=float,
              default=None)
@click.option('--pieces', help='Number of snailgate pieces', type=int, default=1)
@click.option('--pieces-size', help='Size of each snailgate piece', type=float, default=1.0)
@click.option('--bradius-last', help='Radius of each main buoy', default=0.1, type=float)
@click.option('--bradius-intermediate', help='Buoyant radius of each intermediate vertex', default=0.00, type=float)
@click.option('--curvature-rope', help='Use rope connecting endpoints of folded piece, adding curvature to the piece', is_flag=True)
@click.option('--curvature', help='Value that summarizes the curvature of each snailgate piece', type=float, default=0.1)
@click.option('--edge-splits', help='Edge splits', type=int, default=1)
@click.option('--vertical-folded-offset', help='Vertical offset when folded', type=float, default=0.005)
@click.option('--water-level', help='Starting water level', default=0.01, type=float)
@click.option('--leveling-buoy', help='Use buoy on the far right of the structure to help leveling the structure and give base to other structures above', is_flag=True)
@click.option('--distance-leveling-buoy', help='Distance between snailgate structure and leveling buoy', type=float, default=2.00)
@click.option('--horizontal-rope-reduction', help='Distance between snailgate structure and leveling buoy', type=float, default=1.00)
@click.option('--spring-buoys-connection', help='Connection between the two big buoys made with spring', is_flag=True)
@click.option('--diagonal-rope', help='Use diagonal rope connection bottom right to top left buoy', is_flag=True)
@click.option('--leveling-buoy-ground-rope', help='Use rope between right ground vertex (origin) to top right buoys', is_flag=True)
@click.option('--horizontal-rope', help='Use rope between right ground vertex (origin) to top right buoys', is_flag=True)
@click.option('--split-buoys', help='Instead of using big buoys, replace them by splitting the horizontal rope into smaller pieces and adding small buoys to them', type=int)
@click.option('--split-buoys-same-size', help='All big buoys with same size', is_flag=True)
@click.option('--open-in-browser', is_flag=True)
@click.argument('filename')
def generate_scenario(number_snailgates, long_rope_length, pieces, pieces_size, bradius_last, bradius_intermediate,
                      curvature_rope, curvature, edge_splits, vertical_folded_offset, water_level, leveling_buoy,
                      distance_leveling_buoy, horizontal_rope_reduction, spring_buoys_connection, diagonal_rope,
                      leveling_buoy_ground_rope, horizontal_rope, split_buoys, split_buoys_same_size, open_in_browser, filename):
    scenario = Scenario(water_level)

    # create base vertices
    b1 = hinge_point
    b2 = [hinge_point[0] + distance_leveling_buoy, 0.0]

    # add floor edge
    if spring_buoys_connection:
        scenario.add_vertex(b2, FIXED, 0.0)
        b1_index = -1
        b2_index = 0
    else:
        scenario.add_vertex(b1, FIXED, 0.0)
        scenario.add_vertex(b2, FIXED, 0.0)
        b1_index = 0
        b2_index = 1
        scenario.add_edge([b1_index, b2_index], SPRING)


    # sign decides on which side the structure should be folded (left/right)
    sign = -1

    # create the desired number of snailgates layers
    for i in range(0, number_snailgates):

        if diagonal_rope:
            a = pieces_size / (2 + curvature)
            height = (2 - curvature) * a
            width = distance_leveling_buoy
            damping_factor = 0.9
            long_rope_length = math.sqrt(height ** 2 + width ** 2) * damping_factor

        b1_index, b2_index = create_snailgate(b1_index, b2_index, bradius_intermediate, bradius_last, curvature_rope,
                                              curvature, horizontal_rope_reduction * distance_leveling_buoy,
                                              edge_splits, leveling_buoy, long_rope_length, pieces, pieces_size,
                                              scenario, vertical_folded_offset, spring_buoys_connection,
                                              leveling_buoy_ground_rope, horizontal_rope, split_buoys,
                                              split_buoys_same_size, sign, i+1)

        distance_leveling_buoy *= horizontal_rope_reduction

        if not split_buoys is None:
            if not split_buoys_same_size:
                bradius_last *= horizontal_rope_reduction
        #sign *= -1

    result = scenario.to_json()
    with open('./scenarios/' + filename, 'w') as outfile:
        json.dump(result, outfile)

    if open_in_browser:
        os.system('open http://localhost:5000?scenario=' + filename)

if __name__ == '__main__':
    generate_scenario()
