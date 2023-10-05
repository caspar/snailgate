import unittest
import numpy as np
import simulatorLib
import scipy as sp
from scipy import optimize

import pdb

class SimulatorLibTests(unittest.TestCase):
    def print_error_info(self, J, approx_J, x):
        for i in range(0, len(x)):
            for j in range(0, len(x)):
                if J[i, j] == 0:
                    abs_error = np.abs(approx_J[i, j] - J[i, j])
                    if abs_error > 1e-5:
                        print("[Warning] verify element:", i, j)
                        print("Actual value:", J[i, j])
                        print("Approximative value:", approx_J[i, j])
                        print("absError: ", abs_error)
                        print("\n")
                else:
                    rel_error = np.abs((approx_J[i, j] - J[i, j]) / J[i, j])
                    # print "relError: ", rel_error

                    if rel_error > 1e-5:
                        print("[Warning] verify element:", i, j)
                        print("Actual value:", J[i, j])
                        print("Approximative value:", approx_J[i, j])
                        abs_error = np.abs(approx_J[i, j] - J[i, j])
                        print("absError: ", abs_error)
                        print("\n")


    # Compute Jacobian and compare it with approximation
    # noinspection PyPep8,PyPep8Naming
    def testJacobian(self):
        # Arrange
        k = 0.01
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example2()
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)

        free_vertices = []
        num_free_vertices = 0
        for i in range(0, len(V)):
            if VP[i] != 1:
                free_vertices.append(i)
                num_free_vertices += 1

        U = np.zeros((num_free_vertices, 4))
        U[:, 0:2] = V[free_vertices]

        x = U.copy().reshape(-1)
        x += np.array([1.81108641, 3.19165332, 6.24289746, 7.83594813,
                       9.40039611, 7.11717461, 6.91116627, 6.85818088])

        # Act
        #approx_J = optimize.slsqp.approx_jacobian(x, simulatorLib.compute_non_linear_system_function, 1e-8, U, k, V, E, EP, EL, VBR, hw, free_vertices)
        approx_J = simulatorLib.compute_approximate_jacobian(x, U, k, V, E, EP, EL, VBR, hw, free_vertices)
        J = simulatorLib.compute_actual_jacobian(x, U, k, V, E, EP, EL, VBR, hw, free_vertices)

        # Assert
        error = approx_J - J
        max_error = np.max(error)

        self.print_error_info(J, approx_J, x)
        self.assertTrue(np.allclose(J, approx_J, 1e-3, 1e-2))
        self.assertAlmostEqual(max_error, 0.0, 4)



    # Compute Jacobian and compare it with approximation
    # noinspection PyPep8,PyPep8Naming
    def testJacobianBuoyancy(self):
        # Arrange
        k = 0.01
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example6()
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)

        free_vertices = []
        num_free_vertices = 0
        for i in range(0, len(V)):
            if VP[i] != 1:
                free_vertices.append(i)
                num_free_vertices += 1

        U = np.zeros((num_free_vertices, 4))
        U[:, 0:2] = V[free_vertices]

        x = U.copy().reshape(-1)
        x += np.array([0.181108641, 0.319165332, 0.624289746, 0.783594813,
                       0.940039611, 0.711717461, 0.691116627, 0.685818088])

        # Act
        # approxJ1 = optimize.slsqp.approx_jacobian(x, simulatorLib.computeNonLinearSystemFunction, 1e-8, U, k, E, VP, EP, EL, hw)
        approx_J = simulatorLib.compute_approximate_jacobian(x, U, k, V, E, EP, EL, VBR, hw, free_vertices)
        J = simulatorLib.compute_actual_jacobian(x, U, k, V, E, EP, EL, VBR, hw, free_vertices)

        # Assert
        error = approx_J - J
        max_error = np.max(error)

        self.print_error_info(J, approx_J, x)
        self.assertTrue(np.allclose(J, approx_J, 1e-3, 1e-2))
        self.assertAlmostEqual(max_error, 0.0, 4)


    # Compute Jacobian and compare it with approximation
    # noinspection PyPep8,PyPep8Naming
    def testJacobianEdgesReturningToWater(self):
        # Arrange
        k = 0.01
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example7()
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)

        free_vertices = []
        num_free_vertices = 0
        for i in range(0, len(V)):
            if VP[i] != 1:
                free_vertices.append(i)
                num_free_vertices += 1

        U = np.zeros((num_free_vertices, 4))
        U[:, 0:2] = V[free_vertices]

        x = U.copy().reshape(-1)
        x += np.array([0.0181108641, 0.0319165332, 0.0624289746, 0.0783594813,
                       0.0940039611, 0.0711717461, 0.0691116627, 0.0685818088,
                       0.092633199, 0.0120143, 0.054602247, 0.032370617,
                       0.051127654, 0.018950587, 0.042475961, 0.087075558,
                       0.091899879, 0.056347778, 0.042607064, 0.043844895
        ])

        # Act
        #approx_J = optimize.slsqp.approx_jacobian(x, simulatorLib.compute_non_linear_system_function, 1e-8, U, k, V, E, EP, EL, VBR, hw, free_vertices)
        approx_J = simulatorLib.compute_approximate_jacobian(x, U, k, V, E, EP, EL, VBR, hw, free_vertices)
        J = simulatorLib.compute_actual_jacobian(x, U, k, V, E, EP, EL, VBR, hw, free_vertices)

        # Assert
        error = approx_J - J
        max_error = np.max(error)


        self.print_error_info(J, approx_J, x)
        self.assertTrue(np.allclose(J, approx_J, 1e-3, 1e-2))
        self.assertAlmostEqual(max_error, 0.0, 4)

    # Compute Jacobian and compare it with approximation
    # noinspection PyPep8,PyPep8Naming
    def testJacobianEdgesUnderground(self):
        # Arrange
        k = 0.01
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example8()
        E, EP, EL = simulatorLib.pre_ordering_of_edges(V, E, EP, EL)

        free_vertices = []
        num_free_vertices = 0
        for i in range(0, len(V)):
            if VP[i] != 1:
                free_vertices.append(i)
                num_free_vertices += 1

        U = np.zeros((num_free_vertices, 4))
        U[:, 0:2] = V[free_vertices]

        x = U.copy().reshape(-1)
        x += np.array([0.0181108641, 0.0319165332, 0.0624289746, 0.0783594813,
                       0.0940039611, 0.0711717461, 0.0691116627, 0.0685818088,
                       0.092633199, 0.0120143, 0.054602247, 0.032370617,
                       0.051127654, 0.018950587, 0.042475961, 0.087075558,
                       0.091899879, 0.056347778, 0.042607064, 0.043844895
        ])

        # Act
        #approx_J = optimize.slsqp.approx_jacobian(x, simulatorLib.compute_non_linear_system_function, 1e-8, U, k, V, E, EP, EL, VBR, hw, free_vertices)
        approx_J = simulatorLib.compute_approximate_jacobian(x, U, k, V, E, EP, EL, VBR, hw, free_vertices)
        J = simulatorLib.compute_actual_jacobian(x, U, k, V, E, EP, EL, VBR, hw, free_vertices)

        # Assert
        error = approx_J - J
        max_error = np.max(error)


        self.print_error_info(J, approx_J, x)
        self.assertTrue(np.allclose(J, approx_J, 1e-3, 1e-2))
        self.assertAlmostEqual(max_error, 0.0, 4)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
