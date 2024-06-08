import unittest
from x4i import exfor_units
from pint import DimensionalityError

class TestX4Units(unittest.TestCase):
    def setUp(self):
        self.ureg=exfor_units.exfor_unit_registry

    def test_create_exfor_values(self):
        """Routine attempts to make each of the EXFOR units"""
        for ex in exfor_units.exfor_units_dict:
            self.assertEqual(1.0 * self.ureg(exfor_units.exfor_pint_unit_map[ex]).magnitude, 1.0)

    def test_simple_conversions(self):
        self.assertAlmostEqual(197.0 * self.ureg('fm*MeV/hbar/c').to(''), self.ureg.Quantity(0.998342951, 'dimensionless')) 

    def test_temperatures(self):
        self.assertAlmostEqual((self.ureg.Quantity(20.0, 'celsius')).to('eV'), self.ureg.Quantity(0.0252617125, 'eV')) 

    def test_our_defined_units(self):
        self.assertEqual(20.0 * self.ureg('fissions/MeV').to('_100fissions/eV'), self.ureg.Quantity(2e-07, '_100fission / electron_volt'))  

    def test_sqrt_units(self):
        lil_gamma = self.ureg.Quantity(7.0, 'squareroot_eV')
        self.assertAlmostEqual((lil_gamma*lil_gamma).to('eV'), self.ureg.Quantity(49.0, 'eV'))

    def test_arb_units(self):
        """just because the units are arbitrary does not mean we can convert them into anything""" 
        self.assertRaises(DimensionalityError, self.ureg.Quantity(20.0, 'arb_units').to, 'eV')