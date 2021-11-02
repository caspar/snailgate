import math
import numpy as np

water_entering_position_matter = True
rho = 1000  # kg/m^3
g = 9.81  # m/s^2
mass_per_meter_of_spring = 1  # kg/m
kappa = 1e6  # N/m
kappa_ground = 1e5
epsilon_ground = 1e-2
W = 1.0  # m (width)


def ground_collision_jacobian(U, free_vertices, vertex_to_free_vertex):
    num_free_vertices = len(U)
    J = np.zeros((4 * num_free_vertices, 4 * num_free_vertices))

    for v in free_vertices:
        index_free_v = vertex_to_free_vertex[v]
        y = U[index_free_v, 1]

        if y >= epsilon_ground:
            continue

        # compute indices where the jacobian will be filled
        index_CF = 4 * index_free_v + 2
        index_v = 4 * index_free_v
        index_y = index_v + 1

        # add derivative to jacobian
        J[index_CF + 1, index_y] += -kappa_ground

    return J

# Compute Jacobian related to boyance forces
# noinspection PyPep8Naming
def buoyancy_jacobian(U, V, VBR, hw, free_vertices, vertex_to_free_vertex):
    num_free_vertices = len(U)
    J = np.zeros((4 * num_free_vertices, 4 * num_free_vertices))

    for i, radius in enumerate(VBR):

        # no point in computing force if no boyance radius or if vertex is fixed
        if VBR[i] <= 0 or vertex_to_free_vertex[i] < 0:
            continue

        index_free_v = vertex_to_free_vertex[i]
        y = U[index_free_v, 1]

        # also, no point in computing derivative if entire structure is above water level
        # TODO: is it OK to consider the derivative 0 in a conditional formula like this?
        # I believe yes, because if we plug y + radius = hw (or y - radius = hw), it results in dF_dy = 0
        if y + radius <= hw:
            continue
        if y - radius >= hw:
            continue

        # information used while computing derivative
        squared_radius = radius * radius
        K = - 2 * rho * g

        # compute forces
        dF_dy = np.zeros(2)
        dF_dy[1] = K * math.sqrt(squared_radius - (hw - y) * (hw - y))

        # compute indices where the jacobian will be filled
        index_F = 4 * index_free_v + 2
        index_v = 4 * index_free_v
        index_y = index_v + 1

        # add derivative to jacobian
        J[index_F:(index_F + 2), index_y] += dF_dy

    return J


# Compute Jacobian related to tensor
# noinspection PyPep8Naming
def tensor_jacobian(U, V, E, EP, EL, free_vertices, vertex_to_free_vertex):
    num_free_vertices = len(U)
    J = np.zeros((4 * num_free_vertices, 4 * num_free_vertices))
    Ks = kappa

    P = V.copy()
    P[free_vertices] = U[:, 0:2]

    dT_dx = np.zeros(2)
    dT_dy = np.zeros(2)

    for e, edge in enumerate(E):
        if EP[e] == 1:
            continue

        v = edge[0]
        vj = edge[1]

        index_free_v = vertex_to_free_vertex[v]
        index_free_vj = vertex_to_free_vertex[vj]

        # no sense in computing anything if vertices are both fixed
        if index_free_v == -1 and index_free_vj == -1:
            continue

        # indices of v_ starts at  4*v_ (+ 0,1,2,3). But the forces are in positions 3 and 4 (4*v_ + 2 or 3)
        # solve for v1:
        x = P[v][0]
        y = P[v][1]
        xj = P[vj][0]
        yj = P[vj][1]

        # direction v-vj: force leaving vj.
        delta_x = (x - xj)
        delta_y = (y - yj)

        # difference_vector = P[v] - P[vj]
        difference_vector = [P[v][0] - P[vj][0], P[v][1] - P[vj][1]]
        l = math.sqrt(difference_vector[0] ** 2 + difference_vector[1] ** 2)

        l0 = EL[e]

        if (EP[e] == 2) and (l0 > l):
            continue

        # Computing dF/dv
        dT_dx[0] = + (Ks * l0 * (-delta_x / l ** 3) * delta_x + Ks * l0 / l - Ks)
        dT_dx[1] = + (Ks * l0 * (-delta_x / l ** 3) * delta_y)
        dT_dy[0] = + (Ks * l0 * (-delta_y / l ** 3) * delta_x)
        dT_dy[1] = + (Ks * l0 * (-delta_y / l ** 3) * delta_y + Ks * l0 / l - Ks)

        # Computing dF/dvj
        dT_dxj = -dT_dx
        dT_dyj = -dT_dy

        # Add dF/dv1 to its position in Jacobian matrix of our nonlinear system
        if index_free_v != -1:
            index_T = 4 * index_free_v + 2
            index_v = 4 * index_free_v

            J[index_T, index_v] += dT_dx[0]
            J[index_T + 1, index_v] += dT_dx[1]

            J[index_T, index_v + 1] += dT_dy[0]
            J[index_T + 1, index_v + 1] += dT_dy[1]

            if index_free_vj != -1:
                index_vj = 4 * index_free_vj

                J[index_T, index_vj] += dT_dxj[0]
                J[index_T + 1, index_vj] += dT_dxj[1]

                J[index_T, index_vj + 1] += dT_dyj[0]
                J[index_T + 1, index_vj + 1] += dT_dyj[1]

        # Copy everything to F2 (force on v2 (vj))
        if index_free_vj != -1:
            index_Tj = 4 * index_free_vj + 2
            index_vj = 4 * index_free_vj

            J[index_Tj, index_vj] -= dT_dxj[0]
            J[index_Tj + 1, index_vj] -= dT_dxj[1]

            J[index_Tj, index_vj + 1] -= dT_dyj[0]
            J[index_Tj + 1, index_vj + 1] -= dT_dyj[1]

            if index_free_v != -1:
                index_v = 4 * index_free_v

                J[index_Tj, index_v] -= dT_dx[0]
                J[index_Tj + 1, index_v] -= dT_dx[1]

                J[index_Tj, index_v + 1] -= dT_dy[0]
                J[index_Tj + 1, index_v + 1] -= dT_dy[1]

    return J


# noinspection PyPep8Naming
def water_pressure_jacobian(U, V, ETW, hw, free_vertices, vertex_to_free_vertex):
    Kw = rho * g * W

    num_free_vertices = len(U)
    J = np.zeros((4 * num_free_vertices, 4 * num_free_vertices))

    P = V.copy()
    P[free_vertices] = U[:, 0:2]

    for edge in ETW:
        v = edge[1]
        vj = edge[0]

        # indices of v_ starts at  4*v_ (+ 0,1,2,3). But the forces are in positions 3 and 4 (4*v_ + 2 or 3)
        # solve for v1:
        x = P[v][0]
        y = P[v][1]
        xj = P[vj][0]
        yj = P[vj][1]

        delta_x = (x - xj)
        delta_y = (y - yj)

        # Different cases 
        if y == yj:
            # Computing dFdv 
            dF_dx = np.zeros(2)
            dF_dx[0] = 0
            dF_dx[1] = Kw / 2 * (hw - (yj + y) / 2)

            dF_dy = np.zeros(2)
            dF_dy[0] = Kw / 2 * (1 / 2 * delta_y - (hw - (yj + y) / 2))
            dF_dy[1] = Kw / 2 * (-1 / 2 * delta_x)

            # Computing dF/dvj
            dF_dxj = - dF_dx.copy()

            dF_dyj = np.zeros(2)
            dF_dyj[0] = Kw / 2 * (1 / 2 * delta_y + (hw - (yj + y) / 2))
            dF_dyj[1] = dF_dy[1]

        elif yj > hw:
            # Edge leaves water
            # Computing dFdx
            dF_dx = np.zeros(2)
            dF_dx[0] = 0
            dF_dx[1] = Kw / 2 * ((hw - y / 2) * y - hw * hw / 2) / delta_y

            dF_dy = np.zeros(2)
            dF_dy[0] = Kw / 2 * (y - hw)
            dF_dy[1] = Kw / 2 * (
                (hw - y) * delta_x / delta_y - ((hw - y / 2) * y - hw * hw / 2) * (delta_x / (delta_y * delta_y)))

            # Computing dF/dvj
            dF_dxj = np.zeros(2)
            dF_dxj[0] = 0
            dF_dxj[1] = Kw / 2 * ((hw - y / 2) * y - hw * hw / 2) / (-delta_y)

            dF_dyj = np.zeros(2)
            dF_dyj[0] = 0
            dF_dyj[1] = Kw / 2 * (((hw - y / 2) * y - hw * hw / 2) * (delta_x / (delta_y * delta_y)))

        elif y > hw:
            # Edge leaves water
            # Computing dFdx
            dF_dx = np.zeros(2)
            dF_dx[0] = 0
            dF_dx[1] = Kw / 2 * (hw * hw / 2 - (hw - yj / 2) * yj) / delta_y

            dF_dy = np.zeros(2)
            dF_dy[0] = 0
            dF_dy[1] = Kw / 2 * (hw * hw / 2 - (hw - yj / 2) * yj) * (-delta_x / (delta_y * delta_y))

            # Computing dF/dvj
            dF_dxj = np.zeros(2)
            dF_dxj[0] = 0
            dF_dxj[1] = Kw / 2 * (hw * hw / 2 - (hw - yj / 2) * yj) / (-delta_y)

            dF_dyj = np.zeros(2)
            dF_dyj[0] = Kw / 2 * (yj - hw) * (-1)
            dF_dyj[1] = Kw / 2 * (
                (yj - hw) * delta_x / delta_y + (hw * hw / 2 - (hw - yj / 2) * yj) * (delta_x / (delta_y * delta_y)))

        else:
            # Computing dF/dv
            dF_dx = np.zeros(2)
            dF_dx[0] = 0
            dF_dx[1] = Kw / 2 * ((hw - y / 2) * y - (hw - yj / 2) * yj) / delta_y

            dF_dy = np.zeros(2)
            dF_dy[0] = Kw / 2 * (hw - y) * (-1)
            dF_dy[1] = Kw / 2 * (
                (hw - y) * (delta_x / delta_y) + ((hw - y / 2) * y - (hw - yj / 2) * yj) * (
                    -delta_x / (delta_y * delta_y)))

            # Computing dF/dvj
            dF_dxj = np.zeros(2)
            dF_dxj[0] = 0
            dF_dxj[1] = Kw / 2 * ((hw - y / 2) * y - (hw - yj / 2) * yj) / (-delta_y)

            dF_dyj = np.zeros(2)
            dF_dyj[0] = Kw / 2 * (yj - hw) * (-1)
            dF_dyj[1] = Kw / 2 * (
                (yj - hw) * delta_x / delta_y + ((hw - y / 2) * y - (hw - yj / 2) * yj) * (
                    delta_x / (delta_y * delta_y)))

        # Add dF/dv1 to its position in Jacobian matrix of our nonlinear system
        index_free_v = vertex_to_free_vertex[v]
        index_free_vj = vertex_to_free_vertex[vj]

        if index_free_v != -1:
            index_F = 4 * index_free_v + 2
            index_v = 4 * index_free_v

            J[index_F:(index_F + 2), index_v] += dF_dx
            J[index_F:(index_F + 2), index_v + 1] += dF_dy

            if index_free_vj != -1:
                index_vj = 4 * index_free_vj

                J[index_F:(index_F + 2), index_vj] += dF_dxj
                J[index_F:(index_F + 2), index_vj + 1] += dF_dyj

        # Copy everything to F2 (force on v2 (vj))
        if index_free_vj != -1:
            index_Fj = 4 * index_free_vj + 2
            index_vj = 4 * index_free_vj

            J[index_Fj:(index_Fj + 2), index_vj] += dF_dxj
            J[index_Fj:(index_Fj + 2), index_vj + 1] += dF_dyj

            if index_free_v != -1:
                index_v = 4 * index_free_v

                J[index_Fj:(index_Fj + 2), index_v] += dF_dx
                J[index_Fj:(index_Fj + 2), index_v + 1] += dF_dy

    return J


# noinspection PyPep8Naming
def finds_origin(V):
    vertices_at_bottom = []
    for i, vertex in enumerate(V):
        if vertex[1] < 1e-5:
            vertices_at_bottom.append(i)

    origin = 0
    max_x = -float("inf")
    for i in vertices_at_bottom:
        if V[i, 0] > max_x:
            max_x = V[i, 0]
            origin = i

    return origin


# Method that verifies the edges that are touching the water and for which we
# should compute water pressure forces
# This method's version assumes the edges are in the correct order, forming
# a path.
# noinspection PyPep8Naming,PyPep8Naming
def edges_touching_water(V, E, EP, VBR, hw):
    ETW = []
    result = []

    exit_position = -float("inf")
    in_water = True

    # continues searching for next edge to touch water until we achieve a point
    # higher than hw
    for i, edge in enumerate(E):
        if EP[i] == 2:
            break

        last_v = edge[0]
        current_v = edge[1]

        if in_water:
            # if some of the vertices is under water, the edge is wet
            if V[last_v, 1] < hw or V[current_v, 1] < hw:
                ETW.append(edge)

            # if the edge is leaving water, time to save our wet edges
            if V[last_v, 1] < hw <= (V[current_v, 1] + VBR[current_v]):
                # set flat correctly, since we are leaving water
                in_water = False

                x1 = V[last_v, 0]
                y1 = V[last_v, 1]
                x2 = V[current_v, 0]
                y2 = V[current_v, 1]

                if hw > V[current_v, 1]:
                    new_exit_position = x2
                else:
                    new_exit_position = x2 - (y2 - hw) * (x2 - x1) / (y2 - y1)

                # verify if
                if not water_entering_position_matter or new_exit_position >= exit_position:
                    result += ETW

                ETW = []

                exit_position = new_exit_position

        else:
            # Entering water level?
            if hw > V[current_v, 1]:
                x1 = V[last_v, 0]
                y1 = V[last_v, 1]
                x2 = V[current_v, 0]
                y2 = V[current_v, 1]

                # if entire edge is below water, entering position is set as current position
                if hw > V[last_v, 1]:
                    enter_position = x2
                else:
                    enter_position = x2 - (y2 - hw) * (x2 - x1) / (y2 - y1)

                # if it is entering to the right of the exit position, it is fine
                if not water_entering_position_matter or enter_position >= exit_position:
                    # then edge is, in fact, wet
                    ETW.append(edge)

                    # set flat correctly, since we are leaving water
                    in_water = True

    return result


# Method that computes Water pressure force in one edge/bar
# noinspection PyPep8Naming
def compute_water_pressure_force_on_edge(edge, V, hw):
    Kw = rho * g * W

    v1 = V[edge[0]]
    v2 = V[edge[1]]

    x1 = v1[0]
    y1 = v1[1]
    x2 = v2[0]
    y2 = v2[1]

    force = np.array([0.0, 0.0])

    # verifies if final vertex is out of water
    y_start = y1 if hw > y1 else hw
    y_end = y2 if hw > y2 else hw

    # if horizontal edge, computation is easier
    if y1 == y2:
        magnitude = Kw * (hw - y1) * (x2 - x1)
        force[0] = 0
        force[1] = magnitude
    else:
        # forces computed according document about our physics model
        force[0] = - Kw * ((hw - y_end / 2) * y_end - (hw - y_start / 2) * y_start)
        force[1] = - force[0] * (x2 - x1) / (y2 - y1)

    # TODO: add new way of computing the same force 
    # forceNew = np.array([0.0, 0.0])
    # %DeltaY = y2 - y1
    # DeltaX = x2 - x1
    # forceNew[0] = Kw * (hw - (y1 + y_end)/2) * (-DeltaY)
    # forceNew[1] = Kw * (hw - (y1 + y_end)/2) * (DeltaX)

    return force


# Method that computes the gravity forces based on a voronoi of surrounding edges 
# for each vertex
# noinspection PyPep8Naming
def compute_gravity_forces(V, E, EL):
    print("V is greater than E:", len(V)>len(E))
    G = np.zeros((len(V), 2))
    weights = [0] * len(V) #previously [None] ??????

    for i, edge in enumerate(E):
        v1 = edge[0]
        v2 = edge[1]

        weight = EL[i] / 2.0 * mass_per_meter_of_spring * g

        weights[v1] = weight
        weights[v2] = weight

    for i, weight in enumerate(weights):
        G[i] = [0, -weight]

    return G


def get_vertex_bottom(centroid, boyant_radius):
    return centroid[1] - boyant_radius


def get_area_not_submerged_by_water(radius, water_height_from_top):
    h = water_height_from_top

    # source: https://en.wikipedia.org/wiki/Circular_segment
    d = radius - h
    theta = 2 * math.acos(d / radius)

    return math.pow(radius, 2) / 2 * (theta - math.sin(theta))


def get_submerged_area(center_y, radius, water_height):
    if center_y + radius <= water_height:
        return math.pi * radius * radius
    if center_y - radius >= water_height:
        return 0

    water_height_from_top = center_y + radius - water_height

    not_submerged_area = get_area_not_submerged_by_water(radius, water_height_from_top)

    return math.pi * radius * radius - not_submerged_area


def get_boyant_force(centroid, boyant_radius, water_height):
    submerged_volume = get_submerged_area(centroid[1], boyant_radius, water_height)
    displaced_mass = submerged_volume * rho * g

    return displaced_mass


# gets the boyancy forces for each vertex touching water
# noinspection PyPep8Naming,PyPep8Naming,PyPep8Naming
def compute_boyancy_forces(V, VBR, hw):
    B = np.zeros((len(VBR), 2))

    for i, vertex in enumerate(V):
        if VBR[i] > 0:
            B[i] = [0, get_boyant_force(vertex, VBR[i], hw)]

    return B


# Method that computes water pressure forces for all edges in water
# noinspection PyPep8Naming,PyPep8Naming
def compute_water_pressure_forces(V, ETW, hw):
    FWP = np.zeros((len(V), 2))

    for edge in ETW:
        edge_force = compute_water_pressure_force_on_edge(edge, V, hw)

        v1 = edge[0]
        v2 = edge[1]

        FWP[v1, :] += edge_force / 2
        FWP[v2, :] += edge_force / 2

    return FWP


# Method that computes collision forces with the ground
# noinspection PyPep8Naming
def compute_ground_collision_forces(V):
    CF = np.zeros((len(V), 2))

    for v, vertex in enumerate(V):

        if vertex[1] < epsilon_ground:
            ground_force = -kappa_ground * (vertex[1] - epsilon_ground)

            CF[v, 1] = ground_force

    return CF


# Method that computes tensor force on edge
# noinspection PyPep8Naming
def compute_tensor_force_on_spring(spring, V, l0):
    v1 = V[spring[0]]
    v2 = V[spring[1]]

    force = np.zeros(2)

    # computing current length
    difference_vector = v2 - v1
    d = math.sqrt(difference_vector[0] ** 2 + difference_vector[1] ** 2)

    # compute force
    magnitude = kappa * (d - l0)
    force[0] = difference_vector[0] / d * magnitude
    force[1] = difference_vector[1] / d * magnitude

    return force


# Method that computes tensor force on rope
# noinspection PyPep8Naming
def compute_tensor_force_on_rope(rope, V, l0):
    v1 = V[rope[0]]
    v2 = V[rope[1]]

    force = np.zeros(2)

    # computing current length
    difference_vector = v2 - v1
    d = math.sqrt(difference_vector[0] ** 2 + difference_vector[1] ** 2)

    if d < l0:
        return force
    else:
        magnitude = kappa * (d - l0)
        force[0] = difference_vector[0] / d * magnitude
        force[1] = difference_vector[1] / d * magnitude

    return force


# Method that computes tensor forces for all ropes
# noinspection PyPep8Naming
def compute_tensor_forces(V, E, EP, EL):
    T = np.zeros((len(V), 2))

    for i in range(0, len(E)):
        edge = E[i]

        v1 = edge[0]
        v2 = edge[1]

        if EP[i] == 0:
            force = compute_tensor_force_on_spring(edge, V, EL[i])
        elif EP[i] == 2:
            force = compute_tensor_force_on_rope(edge, V, EL[i])
        else:
            force = 0.0

        T[v1, 0] += force[0]
        T[v1, 1] += force[1]

        T[v2, 0] += -force[0]
        T[v2, 1] += -force[1]

    return T


# Computes all forces of the system
# noinspection PyPep8Naming
def compute_resulting_forces(V, E, EP, EL, VBR, hw):
    ETW = edges_touching_water(V, E, EP, VBR, hw)
    # print("ETW: ", ETW)

    G = compute_gravity_forces(V, E, EL)
    # G = np.zeros((len(V), 2))

    B = compute_boyancy_forces(V, VBR, hw)
    # B = np.zeros((len(V), 2))

    FWP = compute_water_pressure_forces(V, ETW, hw)
    # print("FWP: ", FWP)

    T = compute_tensor_forces(V, E, EP, EL)
    # print("T: ", T)

    CF = compute_ground_collision_forces(V)
    # print("CF: ", CF)

    R = T + FWP + G + B + CF
    # print("R: ", R)

    return G, B, FWP, T, R
