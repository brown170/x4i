import unittest
from x4i import exfor_dicts


class TestX4Units(unittest.TestCase):

    def setUp(self):
        self.units_dict = exfor_dicts.get_exfor_dict("Data units")
