import unittest
from x4i import exfor_units
import pint


class TestX4Units(unittest.TestCase):

    def test_create_exfor_values(self):
        for ex in exfor_units.exfor_units_dict:
            pint.Unit(exfor_units.exfor_units_dict[ex])
