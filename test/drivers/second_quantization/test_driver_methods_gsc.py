# This code is part of Qiskit.
#
# (C) Copyright IBM 2019, 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" Test Driver Methods """

from typing import List, Optional, Union

import unittest

from test import QiskitNatureTestCase
from qiskit.algorithms import NumPyMinimumEigensolver
from qiskit_nature.algorithms import GroundStateEigensolver
from qiskit_nature.drivers.second_quantization import ElectronicStructureDriver
from qiskit_nature.mappers.second_quantization import JordanWignerMapper
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.problems.second_quantization import ElectronicStructureProblem
from qiskit_nature.transformers import BaseTransformer as LegacyBaseTransformer
from qiskit_nature.transformers.second_quantization import BaseTransformer


class TestDriverMethods(QiskitNatureTestCase):
    """Common driver tests. For H2 @ 0.735, sto3g"""

    def setUp(self):
        super().setUp()
        self.lih = "LI 0 0 0; H 0 0 1.6"
        self.o_h = "O 0 0 0; H 0 0 0.9697"
        self.ref_energies = {"lih": -7.882, "oh": -74.387}
        self.ref_dipoles = {"lih": 1.818, "oh": 0.4615}

    @staticmethod
    def _run_driver(
        driver: ElectronicStructureDriver,
        converter: QubitConverter = QubitConverter(JordanWignerMapper()),
        transformers: Optional[List[Union[LegacyBaseTransformer, BaseTransformer]]] = None,
    ):

        problem = ElectronicStructureProblem(driver, transformers)

        solver = NumPyMinimumEigensolver()

        gsc = GroundStateEigensolver(converter, solver)

        result = gsc.solve(problem)
        return result

    def _assert_energy(self, result, mol):
        self.assertAlmostEqual(self.ref_energies[mol], result.total_energies[0], places=3)

    def _assert_energy_and_dipole(self, result, mol):
        self._assert_energy(result, mol)
        self.assertAlmostEqual(self.ref_dipoles[mol], result.total_dipole_moment[0], places=3)


if __name__ == "__main__":
    unittest.main()
