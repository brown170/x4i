import unittest
from x4i import exfor_units


class TestX4Units(unittest.TestCase):

    def test_create_exfor_values(self):
        """Routine attempts to make each of the EXFOR units"""
        for ex in exfor_units.exfor_units_dict:
            self.assertEqual(1.0 * exfor_units.exfor_unit_registry(exfor_units.exfor_pint_unit_map[ex]).magnitude, 1.0)
