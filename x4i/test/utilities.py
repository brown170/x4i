# Copyright (c) 2011, Lawrence Livermore National Security, LLC. Produced at
# the Lawrence Livermore National Laboratory. Written by David A. Brown
# <brown170@llnl.gov>.
#
# LLNL-CODE-484151 All rights reserved.
#
# This file is part of EXFOR Interface (x4i)
#
# Please also read the LICENSE.txt file included in this distribution, under
# "Our Notice and GNU General Public License".
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License (as published by the
# Free Software Foundation) version 2, dated June 1991.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# terms and conditions of the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
################################################################################
#
# Changes since LLNL release (x4i-1.0):
#
#   0.     rework __str__ function of an X4DataSet so that can handle sliight differences in treatmeant of str() on floats between py3 & py4    fix bug in table fuzzy-diff    use new fuzzy-diff everywhere (David Brown <dbrown@bnl.gov>, 2018-12-06T15:47:57)
#   1.     need fuzzy diff of tables since py2 & py3 do floats very slightly differently (David Brown <dbrown@bnl.gov>, 2018-12-06T13:14:27)
#
################################################################################


import unittest


class TestCaseWithTableTests(unittest.TestCase):

    def assertRowsAlmostEqual(self, r1, r2):
        self.assertEqual(len(r1), len(r2))
        for j in range(len(r1)):
            c1 = r1[j]
            c2 = r2[j]
            if c1 is None:
                self.assertIsNone(c2)
            elif c2 is None:
                self.assertIsNone(c1)
            else:
                self.assertAlmostEqual(c1, c2, places=3)

    def assertTablesAlmostEqual(self, table1, table2):

        def float_or_none(s):
            try:
                return float(s)
            except ValueError:
                return None

        def split_header_data(t):
            header = []
            data = []
            for line in t.split('\n'):
                if isinstance(line, str) and line.strip().startswith('#'):
                    header.append(line.strip())
                elif isinstance(line, str) and line.strip() == "":
                    pass
                else:
                    data.append([float_or_none(x) for x in line.split()])
            return header, data

        t1h, t1d = split_header_data(table1)
        t2h, t2d = split_header_data(table2)
        self.assertEqual(t1h, t2h)
        self.assertEqual(len(t1d), len(t2d))
        for i in range(len(t1d)):
            self.assertRowsAlmostEqual(t1d[i], t2d[i])
