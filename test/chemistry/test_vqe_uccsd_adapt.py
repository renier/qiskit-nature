# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" Test of the Adaptive VQE implementation with the adaptive UCCSD variational form """

import unittest
from test.aqua.common import QiskitAquaTestCase

from qiskit import Aer
from qiskit.aqua import aqua_globals
from qiskit.aqua.components.optimizers import L_BFGS_B
from qiskit.aqua.operators.op_converter import to_weighted_pauli_operator
from qiskit.aqua.operators.weighted_pauli_operator import Z2Symmetries
from qiskit.chemistry import FermionicOperator
from qiskit.chemistry.aqua_extensions.algorithms.adaptive import VQEAdapt
from qiskit.chemistry.aqua_extensions.components.initial_states import HartreeFock
from qiskit.chemistry.aqua_extensions.components.variational_forms import UCCSDAdapt
from qiskit.chemistry.drivers import PySCFDriver, UnitsType


class TestVQEAdaptUCCSD(QiskitAquaTestCase):
    """ Test Adaptive VQE with UCCSD"""
    def setUp(self):
        super().setUp()
        # np.random.seed(50)
        self.seed = 50
        aqua_globals.random_seed = self.seed
        driver = PySCFDriver(atom='H .0 .0 .0; H .0 .0 0.735',
                             unit=UnitsType.ANGSTROM,
                             basis='sto3g')
        molecule = driver.run()
        self.num_particles = molecule.num_alpha + molecule.num_beta
        self.num_spin_orbitals = molecule.num_orbitals * 2
        ferOp = FermionicOperator(h1=molecule.one_body_integrals, h2=molecule.two_body_integrals)
        map_type = 'PARITY'
        qubitOp = ferOp.mapping(map_type)
        self.qubitOp = Z2Symmetries.two_qubit_reduction(to_weighted_pauli_operator(qubitOp),
                                                        self.num_particles)
        self.num_qubits = self.qubitOp.num_qubits
        self.init_state = HartreeFock(self.num_qubits, self.num_spin_orbitals, self.num_particles)

    def test_uccsd_adapt(self):
        self.var_form_base = UCCSDAdapt(self.num_qubits, 1, self.num_spin_orbitals,
                                        self.num_particles, initial_state=self.init_state)
        # assert that the excitation pool exists
        self.assertIsNotNone(self.var_form_base.excitation_pool)
        # assert that the hopping ops list has been reset to be empty
        self.assertEqual(self.var_form_base._hopping_ops, [])

    def test_vqe_adapt(self):
        """ VQEAdapt test """
        # this is not nice, but unfortunately these two tests rely on each other
        # thus, this line ensures that self.var_form_base exists where it should
        self.test_uccsd_adapt()
        backend = Aer.get_backend('statevector_simulator')
        optimizer = L_BFGS_B()
        algorithm = VQEAdapt(self.qubitOp, self.var_form_base, optimizer,
                             self.var_form_base.excitation_pool, threshold=0.00001, delta=0.1)
        result = algorithm.run(backend)
        self.assertAlmostEqual(result['energy'], -1.85727503, places=2)
        self.assertIn('num_iterations', result)
        self.assertIn('final_max_grad', result)
        self.assertIn('finishing_criterion', result)


if __name__ == '__main__':
    unittest.main()
