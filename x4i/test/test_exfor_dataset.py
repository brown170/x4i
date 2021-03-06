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
#   0.     get rid of commented out debugging statements (David Brown <dbrown@bnl.gov>, 2018-12-06T16:35:07)
#   1.     rework append() algorithm to throw exceptions instead of simply whining (David Brown <dbrown@bnl.gov>, 2018-12-06T16:34:27)
#   2.     rework __str__ function of an X4DataSet so that can handle sliight differences in treatmeant of str() on floats between py3 & py4
#          fix bug in table fuzzy-diff
#          use new fuzzy-diff everywhere (David Brown <dbrown@bnl.gov>, 2018-12-06T15:47:57)
#   3.     improve readability (David Brown <dbrown@bnl.gov>, 2018-12-06T00:19:18)
#   4.     formatting improvements (David Brown <dbrown@bnl.gov>, 2018-12-05T21:20:27)
#   5.     no xmlrunner for now (David Brown <dbrown@bnl.gov>, 2018-12-04T22:06:10)
#   6.     from __future__ imports missing (David Brown <dbrown@bnl.gov>, 2018-12-04T18:36:38)
#   7.     Python3.X compatibility  (David Brown <dbrown@bnl.gov>, 2018-11-16T21:37:15)
#   8.     tweak paths again (David Brown <dbrown@bnl.gov>, 2014-09-15T14:25:41)
#   9.     forgot the index (David Brown <dbrown@bnl.gov>, 2014-09-15T14:22:33)
#   10.     tweak test data paths (David Brown <dbrown@bnl.gov>, 2014-09-15T14:19:36)
#   11.     fix goofed up unittest (David Brown <dbrown@bnl.gov>, 2014-02-13T14:38:24)
#   12.     small database for unit testing (David Brown <dbrown@bnl.gov>, 2014-02-04T17:31:06)
#   13.     add sort() function so that if entries retrieve in a different order, the test won't fail (David Brown <dbrown@bnl.gov>, 2013-10-10T14:24:09)
#   14.     streamlining X4Entry initialization, hopefully also squashing bugs along the way (David Brown <dbrown@bnl.gov>, 2013-06-19T12:02:54)
#   15.     add optional call to XML test runner (David Brown <dbrown@bnl.gov>, 2012-01-23T19:09:00)
#
################################################################################

from __future__ import print_function, division
import os
import unittest

# Set up the paths to x4i & friends
from x4i import exfor_manager
from x4i import exfor_entry
from x4i import exfor_dataset
from x4i.test import __path__
from x4i.test.utilities import TestCaseWithTableTests

testDBPath = __path__[0] + os.sep + 'data'
testIndexFileName = testDBPath + os.sep + 'index.tbl'


class TestX4DataSet(TestCaseWithTableTests):

    def setUp(self):
        db = exfor_manager.X4DBManagerPlainFS(datapath=testDBPath, database=testIndexFileName)
        l = db.retrieve(quantity='SIG', target='PU-239', reaction='N,2N', rawEntry=True)
        self.ds = {}
        for k in l:
            self.ds.update(exfor_entry.X4Entry(l[k]).getSimplifiedDataSets(True))

    def test_append(self):
        d = exfor_dataset.X4DataSet()
        keys = list(self.ds.keys())
        keys.sort()
        keys.reverse()
        for k in keys:
            try:
                d.append(self.ds[k])
            except TypeError:
                pass
        d.sort()
        answer = '''#  Authors:   N, o, n, e
#  Title:     None
#  Year:      None
#  Institute: None
#  Reference: None
#  Subent:    ????????
#  Reaction:  Cross section for 239Pu(n,2n)238Pu
#        Energy        Data          d(Energy)     d(Data)
#        MeV           barns         MeV           barns         
        6.481         0.1009        0.2239        0.03081
        6.49          0.024         0.085         0.063
        6.5           0.419         0.0           0.053
        6.942         0.1261        0.1894        0.02015
        7.01          0.049         0.08          0.05
        7.1           0.451         0.0           0.06
        7.49          0.1525        0.2412        0.01422
        7.52          0.054         0.075         0.058
        8.0           0.49          0.0           0.057
        8.03          0.177         0.075         0.07
        8.084         0.2263        0.2582        0.0154
        8.54          0.275         0.07          0.054
        8.751         0.2669        0.293         0.01659
        9.0           0.51          0.0           0.09
        9.04          0.249         0.065         0.041
        9.504         0.3029        0.3446        0.01659
        9.55          0.354         0.065         0.056
        10.06         0.415         0.06          0.039
        10.34         0.3508        0.3961        0.02014
        10.56         0.411         0.06          0.07
        11.07         0.356         0.055         0.079
        11.34         0.3561        0.4307        0.02015
        11.57         0.418         0.055         0.049
        12.08         0.455         0.055         0.076
        12.45         0.2951        0.534         0.01776
        12.58         0.318         0.05          0.132
        13.09         0.588         0.05          0.148
        13.1          0.641         0.0           0.038
        13.77         0.2284        0.603         0.01539
        13.8          0.228         0.0           0.006384
        14.0          0.219         0.0           0.007884
        14.8          0.214         0.0           0.002996
        15.33         0.1558        0.7231        0.0154
        17.19         0.1178        0.8438        0.008262
        19.34         0.1025        1.068         0.007097
        '''
        self.assertTablesAlmostEqual(str(d), answer)


if __name__ == "__main__":
    # try:
    #     import xmlrunner
    #     unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-results'))
    # except ImportError:
    unittest.main()
    print()
    print()
