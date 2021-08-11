import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection


# Draw simulation
# noinspection PyPep8Naming
def draw_simulation(U, F, E, EP, hw, water_speed, k, step_size=100):
    num_iterations = len(U)

    # print "Started drawing"

    ion()
    show()

    # print "After show()"

    for i in range(0, num_iterations, step_size):
        # print "Initiated iteration"
        V = U[i]
        forces = F[i]

        plot_watergate_setup(V, E, EP, hw)
        draw_vectors(V, forces)

        pause()

        hw += water_speed * k * step_size

        # print "Finished iteration"


# Draw vectors in the test viewer
# noinspection PyPep8Naming
def draw_vectors(V, F):
    init = False
    tangent_vectors = np.empty((1, 2))

    F /= 1e4

    for i, vertex in enumerate(V):
        force = F[i]

        vp = np.concatenate((vertex, force))

        if not init:
            init = True
            tangent_vectors = vp
            continue

        tangent_vectors = np.vstack((tangent_vectors, vp))

    X, Y, U, V = zip(*tangent_vectors)
    ax = plt.gca()
    ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1)


# Plot Watergate setup
# noinspection PyPep8Naming
def plot_watergate_setup(V, E, EP, hw):
    fig, ax = plt.subplots(1, 1)

    # construct segments that we should draw
    segments = []
    seg_colors = []
    for i, edge in enumerate(E):
        segments.append([V[edge[0], :].tolist(), V[edge[1], :].tolist()])
        if EP[i] == 0:
            seg_colors.append('k')
        else:
            seg_colors.append('m')

    lc = LineCollection(segments, colors=seg_colors, linewidths=2, antialiased=True)
    ax.add_collection(lc)

    # add the water level
    min_x = np.min(V[:, 0])
    max_x = np.max(V[:, 0])
    min_y = np.min(V[:, 1])
    max_y = np.max(V[:, 1])
    range_x = max_x - min_x
    range_y = max_y - min_y
    t = np.arange(min_x - .5, max_x + .5, 0.001)
    ax.plot(t, hw + 0.01 * range_y * np.sin(10 / (max_x - min_x) * np.pi * t), color='b')

    # we'll also plot some markers and numbers for the nodes
    ax.plot(V[:, 0], V[:, 1], 'ok', ms=range_x / 3)
    for i, vertex in enumerate(V):
        ax.annotate(str(i), xy=vertex, xytext=(range_x / 2, range_x / 2), textcoords='offset points', fontsize='large')

    plt.xlim([np.min(V[:, 0]) - .5, np.max(V[:, 0]) + .5])
    plt.ylim([np.min(V[:, 1]) - .5, np.max(V[:, 1]) + .5])

    plt.gca().set_aspect('equal', adjustable='box')

    return fig, ax


# show plot
def show():
    plt.show()


# makes matplotlib non blocking
def ion():
    plt.ion()


# pause so figure can refresh
def pause():
    plt.pause(0.001)
    plt.close()
