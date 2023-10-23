#!/usr/bin/env python
import time
import numpy as np
import scipy as sp
from scipy import optimize
import forcesLib
import geometryLib

damping = 0.8


# Method that preorders edges in such a way that they follow a natural order of vertices and edges from the initial
# floor vertex
# noinspection PyPep8Naming
def pre_ordering_of_edges(V, E, EP, EL):
    new_edges = []
    new_edges_tag = []
    new_edges_length = []
    ropes_indices = []

    # searches for origin
    origin = forcesLib.finds_origin(V)

    # starts at the origin
    current_v = origin

    # continues searching for next edge to touch water until we achieve a point
    # higher than hw
    while True:
        last_edge = new_edges[-1] if len(new_edges) > 0 else [-1, -1]

        # find all edges connecting to the current vertex
        connected_edge = [-1, -1]
        connected_edge_index = -1
        for i, edge in enumerate(E):
            if geometryLib.equal_edges(edge, last_edge):
                continue

            if EP[i] == 2:
                continue

            if edge[0] == current_v:
                connected_edge = edge
                connected_edge_index = i
                break

            # flip if necessary
            if edge[1] == current_v:
                connected_edge = [edge[1], edge[0]]
                connected_edge_index = i
                break

        # if no connected edge was found, simply leave
        if connected_edge_index == -1:
            break

        # Add new edge
        new_edges.append(connected_edge)
        new_edges_tag.append(EP[connected_edge_index])
        new_edges_length.append(EL[connected_edge_index])

        # update V
        current_v = connected_edge[1]

    for i, edge in enumerate(E):
        if EP[i] == 2:
            new_edges.append(E[i])
            new_edges_tag.append(EP[i])
            new_edges_length.append(EL[i])

    return new_edges, new_edges_tag, new_edges_length


# noinspection PyPep8Naming,PyUnusedLocal
def compute_actual_jacobian(x, previous_U, k, V, E, EP, EL, VBR, hw, free_vertices):
    num_free_vertices = len(x) // 4
    num_var = 4 * num_free_vertices
    JF = np.zeros((num_var, num_var))
    U = x.reshape((num_free_vertices, 4))

    I = np.identity(num_var)

    # construct map from vertices to free vertices
    vertex_to_free_vertex = [-1 for _ in range(len(V))]
    for i in range(0, len(free_vertices)):
        vertex_to_free_vertex[free_vertices[i]] = i

    # current positions
    P = V.copy()
    P[free_vertices] = U[:, 0:2]

    # add forces part
    ETW = forcesLib.edges_touching_water(P, E, EP, VBR, hw)
    JF += forcesLib.tensor_jacobian(U, V, E, EP, EL, free_vertices, vertex_to_free_vertex)
    JF += forcesLib.water_pressure_jacobian(U, V, ETW, hw, free_vertices, vertex_to_free_vertex)
    JF += forcesLib.buoyancy_jacobian(U, V, VBR, hw, free_vertices, vertex_to_free_vertex)
    JF += forcesLib.ground_collision_jacobian(U, free_vertices, vertex_to_free_vertex)

    JF *= damping

    # add velocity derivatives:
    for i in range(0, num_free_vertices):
        index_vi_func = 4 * i
        index_vi = 4 * i + 2

        JF[index_vi_func, index_vi] = 1.0  # x coordinate
        JF[index_vi_func + 1, index_vi + 1] = 1.0  # y coordinate

    # Remember, the jacobian we want is the derivative of F(U^{n+1}) = U^{n+1} - U^n - k F(U^{n})
    R = I - k * JF

    return R


# Approximation of Jacobian for testing purposes
# noinspection PyPep8Naming
def compute_approximate_jacobian(x, previous_U, k, V, E, EP, EL, VBR, hw, free_vertices):
    h = 1e-7
    num_var = len(x)
    J = np.zeros((num_var, num_var))

    for i in range(0, num_var):
        x_perturb = x.copy()
        x_perturb[i] += h
        fx_perturb_plus = compute_non_linear_system_function(x_perturb, previous_U, k, V, E, EP, EL, VBR, hw,
                                                             free_vertices)

        x_perturb = x.copy()
        x_perturb[i] -= h
        fx_perturb_minus = compute_non_linear_system_function(x_perturb, previous_U, k, V, E, EP, EL, VBR, hw,
                                                              free_vertices)

        diff = fx_perturb_plus - fx_perturb_minus
        J[:, i] = diff / (2 * h)

    return J


# Compute function G(x), which is the left hand side of the system G(x) = 0 we
# are trying to solve.  Notice that the system is actually representing an
# iteration of the Backward Euler method: U^{n+1} - U^n - k F(U^{n}) = 0
# noinspection PyPep8Naming
def compute_non_linear_system_function(x, previous_U, k, V, E, EP, EL, VBR, hw, free_vertices):
    num_vertices = len(x) // 4
    U_n = previous_U
    U_np = x.reshape((num_vertices, 4))

    func_result = compute_function(U_np, V, E, EP, EL, VBR, hw, free_vertices)

    # applying damping to velocities
    damped_Un = U_n.copy()
    for i in range(0, num_vertices):
        func_result[i, 2] *= damping
        func_result[i, 3] *= damping
        damped_Un[i, 2] *= damping
        damped_Un[i, 3] *= damping

    result = U_np - k * func_result[:, 0:4] - damped_Un

    return result.reshape(-1)


# Simple implementation of Newtons method.
# noinspection PyPep8Naming,PyUnusedLocal
def solve_non_linear_system(U, V, E, VP, EP, EL, VBR, hw, k, free_vertices):
    previous_U = U
    x0 = U.reshape(-1)
    num_free_v = len(x0) // 4
    got_it = True

    x, infodict, ier, mesg = sp.optimize.fsolve(compute_non_linear_system_function, x0,
                               args=(previous_U, k, V, E, EP, EL, VBR, hw, free_vertices),
                               fprime=compute_actual_jacobian, xtol=1e-5, full_output=1)

    if not ier == 1:
        print("Warning from fsolve! Will find solution explicitly")
        print(mesg)
        x = x0
        got_it = False

    return x.reshape((num_free_v, 4)), got_it


# This method computes the right hand side of the ODE being solved. Notice that
# it is not only the forces, since we are solving a system of first order
# equations instead of the original second order ODE
# noinspection PyPep8Naming
def compute_function(U, V, E, EP, EL, VBR, hw, free_vertices):
    num_free_vertices = len(free_vertices)
    FU = np.zeros((num_free_vertices, 12))

    # First two rows are actually previous velocities
    FU[:, 0:2] = U[:, 2:4]

    # Compute the current position of all vertices using our maps
    cur_v = V.copy()
    cur_v[free_vertices] = U[:, 0:2]

    # The last two position are the forces on each vertex
    gravity_forces, boyant_forces, water_pressure_forces, tensor_forces, total_forces = \
        forcesLib.compute_resulting_forces(cur_v, E, EP, EL, VBR, hw)

    for j in range(0, num_free_vertices):
        vertex_index = free_vertices[j]

        FU[j, 2:4] = total_forces[vertex_index]
        FU[j, 4:6] = water_pressure_forces[vertex_index]
        FU[j, 6:8] = tensor_forces[vertex_index]
        FU[j, 8:10] = gravity_forces[vertex_index]
        FU[j, 10:12] = boyant_forces[vertex_index]

    # Draw force vectors
    # plotLib.drawVectors(V, Forces)

    return FU


# noinspection PyPep8Naming,PyPep8Naming
def batch_result(U, FU, wl, start, end, total_steps):
    print('getting batch from', start, end)
    return U[start:end, :, 0:2], FU[start:end, :, 2:12], wl[start:end], total_steps


def verify_equilibrium(velocity_and_forces, tolerance):
    max_value = np.linalg.norm(velocity_and_forces.reshape(-1), np.inf)

    if max_value < tolerance:
        return True
    else:
        print("Max value not in equilibrium: ", max_value)
        return False


# run Backward Forward Euler to simulate watergate system
# noinspection PyPep8Naming
def implicit_simulation(V, E, VP, EP, EL, VBR, hw, water_speed=0.0, k=0.01, max_iterations=1000, batch_duration=1):
    num_v = len(V)  # number of vertices

    E, EP, EL = pre_ordering_of_edges(V, E, EP, EL)

    # construct map from free vertices to vertices and vice versa
    free_vertices = []
    num_free_vertices = 0
    for i in range(0, len(V)):
        if VP[i] != 1:
            free_vertices.append(i)
            num_free_vertices += 1

    # U contains, for each (free) vertex, pos X,Y and velocities VX,VY, where V* is
    # the velocity in coordinate *
    U = np.zeros((max_iterations, num_free_vertices, 4))
    P = np.zeros((max_iterations, num_v, 2))
    forces = np.zeros((max_iterations, num_v, 12))
    FU = np.zeros((max_iterations, num_free_vertices, 12))
    wl = np.zeros(max_iterations)

    # construct U0 (velocity is already 0). Set positions equal to initial
    U[0, :, 0:2] = V[free_vertices]
    P[0] = V.copy()

    last_emit_time = time.time()
    last_emitted = 0

    # turn plotting on
    # plotLib.ion()
    # plotLib.show()

    for n in range(0, max_iterations - 1):
        print("Water level: " + str(hw))

        # plot current setup
        # plotLib.plotWatergateSetup(U[n, :, 0:2], E, EP, hw)

        # run iteration of Backward Euler
        # compute function and run Newtons method to find new U
        FU[n] = compute_function(U[n], V, E, EP, EL, VBR, hw, free_vertices)

        # applying damping to velocities for initial guess
        damped_Un = U[n].copy()
        damped_func_result = FU[n, :, 0:4].copy()
        for i in range(0, len(free_vertices)):
            damped_func_result[i, 2] *= damping
            damped_func_result[i, 3] *= damping
            damped_Un[i, 2] *= damping
            damped_Un[i, 3] *= damping

        initial_guess = damped_Un + 0.2 * k * damped_func_result

        result, got_it = solve_non_linear_system(initial_guess, V, E, VP, EP, EL, VBR, hw, k, free_vertices)
        if got_it:
            U[n + 1] = result
        else:
            U[n + 1] = initial_guess

        P[n + 1] = V.copy()
        P[n + 1, free_vertices] = U[n + 1, :, 0:2]
        forces[n] = np.zeros((num_v, 12))
        forces[n, free_vertices] = FU[n]
        wl[n] = hw

        # pause and update plot
        # plotLib.pause()
        # if n == 0:
        #    time.sleep(1)

        # compute displacement update between new U and previous U
        # displacement = U[n + 1] - U[n]
        # noinspection PyTypeChecker
        # distance = np.sum(np.abs(displacement) ** 2, axis=-1) ** (1. / 2)

        if time.time() - last_emit_time >= batch_duration or n == max_iterations - 2:
            yield batch_result(P, forces, wl, last_emitted, n, max_iterations)
            last_emitted = n
            last_emit_time = time.time()

        # if small distance, halts
        # if np.max(distance) < 1e-15:
        #    print("Finished: left because was in equilibrium")
        #    print("Iteration:", n)
        #    print("Displacement:", np.max(distance))
        #    yield batch_result(P, forces, wl, last_emitted, n, max_iterations)
        #    break

        in_equilibrium = verify_equilibrium(FU[n, :, 0:4], 100.0)

        if in_equilibrium:
            # computing new water level
            hw += water_speed * k


# Simulation is actually done by solving the ODE: w * x''(t) = F(x), where w is
# weight (initially considered as '1'), x is position of the node and F(x) is
# the force on the node.
# k = time step
# noinspection PyPep8Naming
def simulate(V, E, VP, EP, EL, VBR, hw, water_speed=0.0, k=0.0001, max_iterations=10000, batch_duration=1):
    num_v = len(V)  # number of vertices

    E, EP, EL = pre_ordering_of_edges(V, E, EP, EL)

    # construct map from free vertices to vertices and vice versa
    free_vertices = []
    num_free_vertices = 0
    for i in range(0, len(V)):
        if VP[i] != 1:
            free_vertices.append(i)
            num_free_vertices += 1

    # U contains, for each (free) vertex, pos X,Y and velocities VX,VY, where V* is
    # the velocity in coordinate *
    U = np.zeros((max_iterations, num_free_vertices, 4))
    P = np.zeros((max_iterations, num_v, 2))
    forces = np.zeros((max_iterations, num_v, 12))
    FU = np.zeros((max_iterations, num_free_vertices, 12))
    wl = np.zeros(max_iterations)

    # construct U0 (velocity is already 0). Set positions equal to initial
    U[0, :, 0:2] = V[free_vertices]
    P[0] = V.copy()

    last_emit_time = time.time()
    last_emitted = 0

    # turn plotting on
    # plotLib.ion()
    # plotLib.show()

    for n in range(0, max_iterations - 1):
        # run Forward Euler
        FU[n] = compute_function(U[n], V, E, EP, EL, VBR, hw, free_vertices)
        wl[n] = hw
        #  print(FU[n].shape)
        #  print(FU[n, :].shape, FU[n, :, 0:4].shape)

        # applying damping to velocities
        damped_Un = U[n].copy()
        damped_func_result = FU[n, :, 0:4].copy()
        for i in range(0, len(free_vertices)):
            damped_func_result[i, 2] *= damping
            damped_func_result[i, 3] *= damping
            damped_Un[i, 2] *= damping
            damped_Un[i, 3] *= damping

        U[n + 1] = damped_Un + k * damped_func_result

        P[n + 1] = V.copy()
        P[n + 1, free_vertices] = U[n + 1, :, 0:2]
        forces[n] = np.zeros((num_v, 12))
        forces[n, free_vertices] = FU[n]

        # pause and update plot
        # plotLib.pause()
        # if n == 0:
        #    time.sleep(1)

        # compute displacement update between new U and previous U
        # displacement = U[n + 1] - U[n]
        # noinspection PyTypeChecker
        # distance = np.sum(np.abs(displacement) ** 2, axis=-1) ** (1. / 2)

        if time.time() - last_emit_time >= batch_duration or n == max_iterations - 2:
            yield batch_result(P, forces, wl, last_emitted, n, max_iterations)
            last_emitted = n
            last_emit_time = time.time()

        # if small distance, halts
        # if np.max(distance) < 1e-15:
        #    print("Finished: left because was in equilibrium")
        #    yield batch_result(P, forces, wl, last_emitted, n, max_iterations)
        #    break

        in_equilibrium = verify_equilibrium(FU[n, :, 0:4], 100.0)

        if in_equilibrium:
            # computing new water level
            hw += water_speed * k


# noinspection PyPep8Naming
def from_json(post_body):
    V = np.array(post_body['verteces'])
    E = np.array(post_body['edges'])
    VP = np.array(post_body['vertexTypes'])
    EP = np.array(post_body['edgeTypes'])
    EL = np.array(post_body['edgeLengths'])
    hw = post_body['waterLevel']
    water_speed = float(post_body.get('waterLevelRaiseRate', "0.0"))
    VBR = np.array(post_body['vertexBoyantRadiai'])
    time_step = float(post_body.get('timeStep', "0.01"))
    max_iterations = int(post_body.get('maxIterations', 1000))
    simulation_method = post_body.get('simulationMethod', "Backward Euler")

    return V, E, VP, EP, EL, hw, VBR, water_speed, time_step, max_iterations, simulation_method


# noinspection PyPep8Naming
def get_edge_lengths(E, V):
    EL = []
    for i, edge in enumerate(E):
        EL.append(geometryLib.distance_between(V[E[i][0]], V[E[i][1]]))

    return EL


# first scenario
# noinspection PyPep8Naming
def setup_original_watergate_example():
    # level of water
    hw = .8

    # setting up vertices
    V = np.zeros((5, 2))
    V[0, :] = np.array([0, 0])
    V[1, :] = np.array([-1.0, 0])
    V[2, :] = np.array([-2.0, 0])
    V[3, :] = np.array([-1.3, .5])
    V[4, :] = np.array([-.6, 1.0])
    print("V: ", V)

    VP = [1, 1, 1, 0, 0]
    print("VP: ", VP)

    VBR = [0, 0, 0, 0, 0]
    print("VBR: ", VBR)

    # setting up edges
    E = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 3]]
    print("E: ", E)

    # setting initial length of every edge
    EL = get_edge_lengths(E, V)

    # ropes have different length
    EL[4] = .8
    print("EL: ", EL)

    EP = [0, 0, 0, 0, 2]
    print("EP: ", EP)

    return V, E, VP, EP, EL, VBR, hw


# second scenario: one extra rope
# noinspection PyPep8Naming
def setup_original_watergate_example2():
    # level of water
    hw = .8

    # setting up vertices
    V = np.zeros((5, 2))
    V[0, :] = np.array([0, 0])
    V[1, :] = np.array([-1.0, 0])
    V[2, :] = np.array([-2.0, 0])
    V[3, :] = np.array([-1.3, .5])
    V[4, :] = np.array([-.6, 1.0])
    print("V: ", V)

    VP = [1, 1, 1, 0, 0]
    print("VP: ", VP)

    VBR = [0, 0, 0, 0, 0]
    print("VBR: ", VBR)

    # setting up edges
    E = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 3], [0, 4]]
    print("E: ", E)

    # setting initial length of every edge
    EL = []
    for i, edge in enumerate(E):
        EL.append(geometryLib.distance_between(V[E[i][0]], V[E[i][1]]))

    # ropes have different length
    EL[4] = .8
    EL[5] = 1.2
    print("EL: ", EL)

    EP = [0, 0, 0, 0, 2, 2]
    print("EP: ", EP)

    return V, E, VP, EP, EL, VBR, hw


# third scenario: one hope in diff position
# noinspection PyPep8Naming
def setup_original_watergate_example3():
    # level of water
    hw = .8

    # setting up vertices
    V = np.zeros((5, 2))
    V[0, :] = np.array([0, 0])
    V[1, :] = np.array([-1.0, 0])
    V[2, :] = np.array([-2.0, 0])
    V[3, :] = np.array([-1.3, .5])
    V[4, :] = np.array([-.6, 1.0])
    print("V: ", V)

    VP = [1, 1, 1, 0, 0]
    print("VP: ", VP)

    VBR = [0, 0, 0, 0, 0]
    print("VBR: ", VBR)

    # setting up edges
    E = [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4]]
    print("E: ", E)

    # setting initial length of every edge
    EL = []
    for i, edge in enumerate(E):
        EL.append(geometryLib.distance_between(V[E[i][0]], V[E[i][1]]))

    # ropes have different length
    EL[4] = 1.5
    print("EL: ", EL)

    EP = [0, 0, 0, 0, 2]
    print("EP: ", EP)

    return V, E, VP, EP, EL, VBR, hw


# forth scenario
# noinspection PyPep8Naming
def setup_original_watergate_example4():
    # level of water
    hw = .8

    # setting up vertices
    V = np.zeros((5, 2))
    V[0, :] = np.array([0, 0])
    V[1, :] = np.array([-1.0, 0])
    V[2, :] = np.array([-2.0, 0])
    V[3, :] = np.array([-1.3, .5])
    V[4, :] = np.array([-.6, 1.0])
    V[:, 0] += 20
    print("V: ", V)

    VP = [1, 1, 1, 0, 0]
    print("VP: ", VP)

    VBR = [0, 0, 0, 0, 0]
    print("VBR: ", VBR)

    # setting up edges
    E = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 3]]
    print("E: ", E)

    # setting initial length of every edge
    EL = []
    for i, edge in enumerate(E):
        EL.append(geometryLib.distance_between(V[E[i][0]], V[E[i][1]]))

    # ropes have different length
    EL[4] = .8
    print("EL: ", EL)

    EP = [0, 0, 0, 0, 2]
    print("EP: ", EP)

    return V, E, VP, EP, EL, hw


# noinspection PyPep8Naming
def setup_original_watergate_example5():
    # level of water
    hw = .8

    # setting up vertices
    V = np.zeros((5, 2))
    V[0, :] = np.array([1, 0])
    V[1, :] = np.array([2.484, 0])
    V[2, :] = np.array([2.224, 1.737])
    V[3, :] = np.array([1.2760795739415784, .9617938888590027])
    V[4, :] = np.array([1.356, 0])
    print("V: ", V)

    VP = [1, 1, 0, 0, 1]
    print("VP: ", VP)

    VBR = [0, 0, 0, 0, 0]
    print("VBR: ", VBR)

    # setting up edges
    E = [[0, 4], [0, 3], [3, 2], [4, 1], [3, 4]]
    print("E: ", E)

    # setting initial length of every edge
    EL = []
    for i, edge in enumerate(E):
        EL.append(geometryLib.distance_between(V[E[i][0]], V[E[i][1]]))

    # ropes have different length
    EL[4] = 0.9
    print("EL: ", EL)

    EP = [0, 0, 0, 0, 2]
    print("EP: ", EP)

    return V, E, VP, EP, EL, hw


# second scenario: one extra rope
# noinspection PyPep8Naming
def setup_original_watergate_example6():
    # level of water
    hw = 0.8

    # setting up vertices
    V = np.zeros((5, 2))
    V[0, :] = np.array([0, 0])
    V[1, :] = np.array([-1.0, 0])
    V[2, :] = np.array([-2.0, 0])
    V[3, :] = np.array([-1.3, .7])
    V[4, :] = np.array([-.6, 1.0])
    print("V: ", V)

    VP = [1, 1, 1, 0, 0]
    print("VP: ", VP)

    VBR = [0, 0, 0, 3.0, 5.0]
    print("VBR: ", VBR)

    # setting up edges
    E = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 3], [0, 4]]
    print("E: ", E)

    # setting initial length of every edge
    EL = []
    for i, edge in enumerate(E):
        EL.append(geometryLib.distance_between(V[E[i][0]], V[E[i][1]]))

    # ropes have different length
    EL[4] = .8
    EL[5] = 1.2
    print("EL: ", EL)

    EP = [0, 0, 0, 0, 2, 2]
    print("EP: ", EP)

    return V, E, VP, EP, EL, VBR, hw


# 7th scenario: springs go out of the water and then return
# noinspection PyPep8Naming
def setup_original_watergate_example7():
    # level of water
    hw = 0.8

    # setting up vertices
    V = np.zeros((8, 2))
    V[0, :] = np.array([0, 0])
    V[1, :] = np.array([-1.0, 0])
    V[2, :] = np.array([-2.0, 0])
    V[3, :] = np.array([-1.3, .7])
    V[4, :] = np.array([-.6, 1.0])
    V[5, :] = np.array([-0.3, 1.0])
    V[6, :] = np.array([0.0, 0.3])
    V[7, :] = np.array([0.5, 0.9])
    print("V: ", V)

    VP = [1, 1, 1, 0, 0, 0, 0, 0]
    print("VP: ", VP)

    VBR = [0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0]
    print("VBR: ", VBR)

    # setting up edges
    E = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 3], [0, 4], [4, 5], [5, 6], [6, 7]]
    print("E: ", E)

    # setting initial length of every edge
    EL = []
    for i, edge in enumerate(E):
        EL.append(geometryLib.distance_between(V[E[i][0]], V[E[i][1]]))

    # ropes have different length
    EL[4] = .8
    EL[5] = 1.2
    print("EL: ", EL)

    EP = [0, 0, 0, 0, 2, 2, 0, 0, 0]
    print("EP: ", EP)

    return V, E, VP, EP, EL, VBR, hw


# 8th scenario: springs go underground
# noinspection PyPep8Naming
def setup_original_watergate_example8():
    # level of water
    hw = 0.8

    # setting up vertices
    V = np.zeros((8, 2))
    V[0, :] = np.array([0, 0])
    V[1, :] = np.array([-1.0, 0])
    V[2, :] = np.array([-2.0, 0])
    V[3, :] = np.array([-1.3, -.7])
    V[4, :] = np.array([-.6, -1.0])
    V[5, :] = np.array([-0.3, 1.0])
    V[6, :] = np.array([0.0, 0.3])
    V[7, :] = np.array([0.5, 0.9])
    print("V: ", V)

    VP = [1, 1, 1, 0, 0, 0, 0, 0]
    print("VP: ", VP)

    VBR = [0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0]
    print("VBR: ", VBR)

    # setting up edges
    E = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 3], [0, 4], [4, 5], [5, 6], [6, 7]]
    print("E: ", E)

    # setting initial length of every edge
    EL = []
    for i, edge in enumerate(E):
        EL.append(geometryLib.distance_between(V[E[i][0]], V[E[i][1]]))

    # ropes have different length
    EL[4] = .8
    EL[5] = 1.2
    print("EL: ", EL)

    EP = [0, 0, 0, 0, 2, 2, 0, 0, 0]
    print("EP: ", EP)

    return V, E, VP, EP, EL, VBR, hw
