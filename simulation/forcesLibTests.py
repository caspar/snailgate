import math
import unittest

import forcesLib
import numpy as np
import simulatorLib


# noinspection PyPep8Naming
class ForcesLibTests(unittest.TestCase):
    # Edges in the Water:
    def testWhichEdgesAreInTheWater(self):
        # Arrange
        hw = 8
        V = np.array([[0, 0], [-10, 0], [-20, 0], [-13, 5], [-6, 10]])
        E = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 3]]
        EP = [0, 0, 0, 0, 2]
        EL = [0, 0, 0, 0, 0]
        VBR = [0.0, 0.0, 0.0, 0.0, 0.0]

        # Act
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)
        edges = forcesLib.edges_touching_water(V, E, EP, VBR, hw)

        # Assert
        true_solution = [[0, 1], [1, 2], [2, 3], [3, 4]]
        self.assertListEqual(true_solution, edges)

    def testWhichEdgesAreInTheWaterWithLowerHeight(self):
        # Arrange
        hw = 4
        V = np.array([[0, 0], [-10, 0], [-20, 0], [-13, 5], [-6, 10]])
        E = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 3]]
        EP = [0, 0, 0, 0, 2]
        EL = [0, 0, 0, 0, 0]
        VBR = [0.0, 0.0, 0.0, 0.0, 0.0]

        # Act
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)
        edges = forcesLib.edges_touching_water(V, E, EP, VBR, hw)

        # Assert
        true_solution = [[0, 1], [1, 2], [2, 3]]
        self.assertListEqual(true_solution, edges)

    def testWhichEdgesAreInTheWaterWithUnorganizedListOfEdges(self):
        # Arrange
        hw = 4
        V = np.array([[0, 0], [-10, 0], [-20, 0], [-13, 5], [-6, 10]])
        E = [[2, 3], [1, 3], [0, 1], [3, 4], [2, 1]]
        EP = [0, 2, 0, 0, 0]
        EL = [0, 0, 0, 0, 0]
        VBR = [0.0, 0.0, 0.0, 0.0, 0.0]

        # Act
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)
        edges = forcesLib.edges_touching_water(V, E, EP, VBR, hw)

        # Assert
        true_solution = [[0, 1], [1, 2], [2, 3]]
        self.assertListEqual(true_solution, edges)

    def testWhichEdgesAreInTheWaterWithEdgeGoingDown(self):
        # Arrange
        hw = 8
        V = np.array([[0, 0], [-10, 0], [-20, 0], [-20, 5], [-25, 3], [-25, 9]])
        E = [[2, 3], [1, 3], [0, 1], [3, 4], [2, 1], [4, 5]]
        EP = [0, 2, 0, 0, 0, 0]
        EL = [0, 0, 0, 0, 0, 0]
        VBR = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # Act
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)
        edges = forcesLib.edges_touching_water(V, E, EP, VBR, hw)

        # Assert
        true_solution = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]
        self.assertListEqual(true_solution, edges)

    def testWhichEdgesAreInTheWaterWithEdgeBehindWaterPolygon(self):
        # Arrange
        hw = 7.8
        V = np.array([[0, 0], [-10, 0], [-20, 0], [-20, 8], [-25, 3], [-25, 9]])
        E = [[2, 3], [1, 3], [0, 1], [3, 4], [2, 1], [4, 5]]
        EP = [0, 2, 0, 0, 0, 0]
        EL = [0, 0, 0, 0, 0, 0]
        VBR = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # Act
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)
        edges = forcesLib.edges_touching_water(V, E, EP, VBR, hw)

        # Assert
        true_solution = [[0, 1], [1, 2], [2, 3]]
        self.assertListEqual(true_solution, edges)

    def testWhichEdgesAreInTheWaterWithEdgeBehindWaterPolygonGoingBackToFront(self):
        # Arrange
        hw = 7.8
        V = np.array([[0, 0], [-10, 0], [-20, 0], [-20, 8], [-25, 3], [-25, 9], [10, 8], [10, 2], [12, 7.9]])
        E = [[2, 3], [1, 3], [0, 1], [3, 4], [2, 1], [4, 5], [5, 6], [6, 7], [7,8]]
        EP = [0, 2, 0, 0, 0, 0, 0, 0, 0]
        EL = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        VBR = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # Act
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)
        edges = forcesLib.edges_touching_water(V, E, EP, VBR, hw)

        # Assert
        true_solution = [[0, 1], [1, 2], [2, 3], [6, 7], [7, 8]]
        self.assertListEqual(true_solution, edges)

    def testWhichEdgesAreInTheWaterWithTwoBuoysLinkedThroughHorizontalEdge(self):
        # Arrange
        hw = 10.2
        V = np.array([[0, 0], [-10, 0], [-10, 10], [0, 10], [0, 20]])
        E = [[0, 1], [1, 2], [2, 3], [3, 4]]
        EP = [0, 0, 0, 0]
        EL = [0, 0, 0, 0]
        VBR = [0.0, 0.0, 0.5, 0.5, 0.0]

        # Act
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)
        edges = forcesLib.edges_touching_water(V, E, EP, VBR, hw)

        # Assert
        true_solution = [[0, 1], [1, 2], [2, 3], [3, 4]]
        self.assertListEqual(true_solution, edges)


    # Water Pressure Forces:

    # Horizontal edges
    def testWPForceOnHorizontalEdgeOnTheGround(self):
        # Arrange
        edge = [0, 1]
        V = np.array([[2.0, 0.0], [0.0, 0.0]])
        hw = 3.0

        # Act
        force = forcesLib.compute_water_pressure_force_on_edge(edge, V, hw)

        # Assert
        true_magnitude = 1000 * 9.81 * 1 * 3 * 2  # rho * g * W * (hw - y) * DeltaX
        self.assertAlmostEqual(force[0], 0.0)
        self.assertAlmostEqual(force[1], -true_magnitude)

    def testWPForceOnHorizontalEdgeOnTheGround2(self):
        # Arrange
        edge = [0, 1]
        V = np.array([[4.0, 0.0], [-1.0, 0.0]])
        hw = 3.0

        # Verify
        force = forcesLib.compute_water_pressure_force_on_edge(edge, V, hw)

        # Assert
        true_magnitude = 1000 * 9.81 * 1 * 3 * 5  # rho * g * W * (hw - y) * DeltaX
        self.assertAlmostEqual(force[0], 0.0)
        self.assertAlmostEqual(force[1], -true_magnitude)

    def testWPForceOnHorizontalEdgeAboveTheGround(self):
        # Arrange
        edge = [0, 1]
        V = np.array([[2.0, 5.0], [0.0, 5.0]])
        hw = 8.0

        # Verify
        force = forcesLib.compute_water_pressure_force_on_edge(edge, V, hw)

        # Assert
        true_magnitude = 1000 * 9.81 * 1 * 3 * 2  # rho * g * W * (hw - y) * DeltaX
        self.assertAlmostEqual(force[0], 0.0)
        self.assertAlmostEqual(force[1], -true_magnitude)

    def testWPForceOnHorizontalEdgeAboveTheGround2(self):
        # Arrange
        edge = [0, 1]
        V = np.array([[4.0, 3.0], [-1.0, 3.0]])
        hw = 10.0

        # Verify
        force = forcesLib.compute_water_pressure_force_on_edge(edge, V, hw)

        # Assert
        true_magnitude = 1000 * 9.81 * 1 * 7 * 5  # rho * g * W * (hw - y) * DeltaX
        self.assertAlmostEqual(force[0], 0.0)
        self.assertAlmostEqual(force[1], -true_magnitude)

    # Diagonal Edges
    def testWPForceOnDiagonalEdge45degrees(self):
        # Arrange
        edge = [0, 1]
        V = np.array([[0.0, 0.0], [2.0, 2.0]])
        hw = 5.0

        # Verify
        force = forcesLib.compute_water_pressure_force_on_edge(edge, V, hw)

        # Assert
        true_magnitude = 1000 * 9.81 * 1.0 / (math.sqrt(2) / 2) * (
            (5.0 - 1.0) * 2.0)  # rho * g * W / sin(45) * [(hw - y/2) * y]_{y1}^{y2}
        self.assertAlmostEqual(force[0], -true_magnitude * math.sqrt(2) / 2)
        self.assertAlmostEqual(force[1], true_magnitude * math.sqrt(2) / 2)

    def testWPForceOnDiagonalEdge30degrees(self):
        # Arrange
        edge = [0, 1]
        V = np.array([[0.0, 0.0], [12.0 / math.sqrt(3), 4.0]])
        hw = 5.0

        # Verify
        force = forcesLib.compute_water_pressure_force_on_edge(edge, V, hw)

        # Assert
        true_magnitude = 1000 * 9.81 * 1.0 / (1.0 / 2) * (
            (5.0 - 2.0) * 4.0)  # rho * g * W / sin(30) * [(hw - y/2) * y]_{y1}^{y2}
        self.assertAlmostEqual(force[0], -true_magnitude / 2)
        self.assertAlmostEqual(force[1], true_magnitude * math.sqrt(3) / 2)

    # Vertical Edges
    def testWPForceOnVerticalEdge(self):
        # Arrange
        edge = [0, 1]
        V = np.array([[0.0, 0.0], [0.0, 2.0]])
        hw = 5.0

        # Verify
        force = forcesLib.compute_water_pressure_force_on_edge(edge, V, hw)

        # Assert
        true_magnitude = 1000 * 9.81 * 1.0 * ((5.0 - 1.0) * 2.0)  # rho * g * W * [(hw - y/2) * y]_{y1}^{y2}

        self.assertAlmostEqual(force[0], -true_magnitude)
        self.assertAlmostEqual(force[1], 0.0)

    def testWPForceOnVerticalEdgeUpDownDirection(self):
        # Arrange
        edge = [0, 1]
        V = np.array([[0.0, 2.0], [0.0, 0.0]])
        hw = 5.0

        # Verify
        force = forcesLib.compute_water_pressure_force_on_edge(edge, V, hw)

        # Assert
        true_magnitude = abs(1000 * 9.81 * 1.0 * -((5.0 - 1.0) * 2.0))  # rho * g * W * [(hw - y/2) * y]_{y1}^{y2}
        self.assertAlmostEqual(force[0], true_magnitude)
        self.assertAlmostEqual(force[1], 0.0)


    def testWPForceOnDiagonalEdgeEnteringWater(self):
        # Arrange
        edge = [0, 1]
        V = np.array([[-5.0, 7.0], [0.0, 2.0]])
        hw = 5.0

        # Verify
        force = forcesLib.compute_water_pressure_force_on_edge(edge, V, hw)

        # Assert
        true_magnitude = abs(1000 * 9.81 * 1.0 / (math.sqrt(2) / 2) * ((5.0 - 1.0)*2 - (5.0 - 2.5)*5))  # rho * g * W * [(hw - y/2) * y]_{y1}^{y2}
        self.assertAlmostEqual(force[0], true_magnitude *  math.sqrt(2) / 2)
        self.assertAlmostEqual(force[1], true_magnitude *  math.sqrt(2) / 2)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
