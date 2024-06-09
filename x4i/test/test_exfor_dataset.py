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
import numpy

# Set up the paths to x4i & friends
from x4i import exfor_manager
from x4i import exfor_entry
from x4i import exfor_dataset
from x4i.test import __path__
from x4i.test.utilities import TestCaseWithTableTests
import pint_pandas

testDBPath = __path__[0] + os.sep + 'data'
testIndexFileName = testDBPath + os.sep + 'index.tbl'
db = exfor_manager.X4DBManagerPlainFS(datapath=testDBPath, database=testIndexFileName)

class TestX4NewDataSet(TestCaseWithTableTests):

    def setUp(self):
        self.frehaut = {}
        for k,v in db.retrieve(ENTRY='21971', rawEntry=True).items():
            self.frehaut[k]=exfor_entry.X4Entry(v)

        self.other = {}
        for k,v in db.retrieve(ENTRY='O1732', rawEntry=True).items():
            self.other[k]=exfor_entry.X4Entry(v)

    def test_easy(self):
        entry = '21971'
        subent = '21971003'
        new_set = exfor_dataset.X4DataSetNew(data=self.frehaut[entry][subent]['DATA'])
        self.assertEqual(new_set.numrows(), 14)
        self.assertEqual(new_set.numcols(), 4)
        self.assertEqual(len(new_set), 14)
        self.assertEqual(new_set.data.shape, (14, 4))
        numpy.testing.assert_array_almost_equal(
            new_set.data.EN.values.numpy_data.tolist(), 
            [  6.49,  7.01,  7.52,  8.03,  8.54,  9.04,  
               9.55, 10.06, 10.56, 11.07, 11.57,
               12.08, 12.58, 13.09])
        numpy.testing.assert_array_almost_equal(
            new_set.data.EN.pint.to('keV').values.numpy_data.tolist(), 
            [    6490.0, 7010.0,  7520.0,  8029.999999999999,
                 8540.0, 9040.0,  9550.0,  10060.0,
                10560.0, 11070.0, 11570.0, 12080.0,
                12580.0, 13090.0])
        self.assertEqual(str(new_set["EN", 1]), '7.01 MeV')
        #self.assertEqual(new_set.sort(), "")
        #self.assertEqual(new_set.append(), "")

    def test_easy_outputs(self):
        entry = '21971'
        subent = '21971003'
        new_set = exfor_dataset.X4DataSetNew(data=self.frehaut[entry][subent]['DATA'])
        # Check these guys work correctly since the tabulate based scheme relies on them
        self.assertListEqual([str(x.units) for x in new_set.data.dtypes.tolist()], ['MeV', 'MeV', 'mb', 'mb'])
        self.assertListEqual(new_set.data.columns.tolist(), ['EN', 'EN-ERR', 'DATA', 'DATA-ERR'])
        # Now check the formatting routines
        self.assertEqual(new_set.to_tabulate(units='stacked'), '\n'.join([
            '+-------+----------+--------+------------+',
            '|    EN |   EN-ERR |   DATA |   DATA-ERR |',
            '|   MeV |      MeV |     mb |         mb |',
            '|-------+----------+--------+------------|',
            '|  6.49 |    0.085 |     24 |         63 |',
            '|  7.01 |    0.08  |     49 |         50 |',
            '|  7.52 |    0.075 |     54 |         58 |',
            '|  8.03 |    0.075 |    177 |         70 |',
            '|  8.54 |    0.07  |    275 |         54 |',
            '|  9.04 |    0.065 |    249 |         41 |',
            '|  9.55 |    0.065 |    354 |         56 |',
            '| 10.06 |    0.06  |    415 |         39 |',
            '| 10.56 |    0.06  |    411 |         70 |',
            '| 11.07 |    0.055 |    356 |         79 |',
            '| 11.57 |    0.055 |    418 |         49 |',
            '| 12.08 |    0.055 |    455 |         76 |',
            '| 12.58 |    0.05  |    318 |        132 |',
            '| 13.09 |    0.05  |    588 |        148 |', 
            '+-------+----------+--------+------------+']))
        self.maxDiff = None
        self.assertEqual(new_set.to_tabulate(units='sbs_paren'), '\n'.join([
            '+------------+----------------+-------------+-----------------+',
            '|   EN (MeV) |   EN-ERR (MeV) |   DATA (mb) |   DATA-ERR (mb) |',
            '|------------+----------------+-------------+-----------------|',
            '|       6.49 |          0.085 |          24 |              63 |',
            '|       7.01 |          0.08  |          49 |              50 |',
            '|       7.52 |          0.075 |          54 |              58 |',
            '|       8.03 |          0.075 |         177 |              70 |',
            '|       8.54 |          0.07  |         275 |              54 |',
            '|       9.04 |          0.065 |         249 |              41 |',
            '|       9.55 |          0.065 |         354 |              56 |',
            '|      10.06 |          0.06  |         415 |              39 |',
            '|      10.56 |          0.06  |         411 |              70 |',
            '|      11.07 |          0.055 |         356 |              79 |',
            '|      11.57 |          0.055 |         418 |              49 |',
            '|      12.08 |          0.055 |         455 |              76 |',
            '|      12.58 |          0.05  |         318 |             132 |',
            '|      13.09 |          0.05  |         588 |             148 |', 
            '+------------+----------------+-------------+-----------------+']))
        self.assertEqual(new_set.to_csv(None), '\n'.join([
            ",EN,EN-ERR,DATA,DATA-ERR",
            '0,6.49 MeV,0.085 MeV,24.0 mb,63.0 mb',
            '1,7.01 MeV,0.08 MeV,49.0 mb,50.0 mb',
            '2,7.52 MeV,0.075 MeV,54.0 mb,58.0 mb',
            '3,8.03 MeV,0.075 MeV,177.0 mb,70.0 mb',
            '4,8.54 MeV,0.07 MeV,275.0 mb,54.0 mb',
            '5,9.04 MeV,0.065 MeV,249.0 mb,41.0 mb',
            '6,9.55 MeV,0.065 MeV,354.0 mb,56.0 mb',
            '7,10.06 MeV,0.06 MeV,415.0 mb,39.0 mb',
            '8,10.56 MeV,0.06 MeV,411.0 mb,70.0 mb',
            '9,11.07 MeV,0.055 MeV,356.0 mb,79.0 mb',
            '10,11.57 MeV,0.055 MeV,418.0 mb,49.0 mb',
            '11,12.08 MeV,0.055 MeV,455.0 mb,76.0 mb',
            '12,12.58 MeV,0.05 MeV,318.0 mb,132.0 mb',
            '13,13.09 MeV,0.05 MeV,588.0 mb,148.0 mb',
            '']))
        self.assertEqual(new_set.to_markdown(), '\n'.join([
            '  EN (MeV)    EN-ERR (MeV)    DATA (mb)    DATA-ERR (mb)',
            '----------  --------------  -----------  ---------------',
            '      6.49           0.085           24               63',
            '      7.01           0.08            49               50',
            '      7.52           0.075           54               58',
            '      8.03           0.075          177               70',
            '      8.54           0.07           275               54',
            '      9.04           0.065          249               41',
            '      9.55           0.065          354               56',
            '     10.06           0.06           415               39',
            '     10.56           0.06           411               70',
            '     11.07           0.055          356               79',
            '     11.57           0.055          418               49',
            '     12.08           0.055          455               76',
            '     12.58           0.05           318              132',
            '     13.09           0.05           588              148']))
        #self.assertEqual(new_set.to_json(), '')  # FIXME
        
    def test_easy_but_with_some_metadata(self):
        entry = '21971'
        subent = '21971003'
        #print(self.frehaut[entry][subent]['BIB']['REACTION'].reactions[' '][0])
        new_set = exfor_dataset.X4DataSetNew(
            data=self.frehaut[entry][subent]['DATA'], 
            reaction=self.frehaut[entry][subent]['BIB']['REACTION'].reactions[' '], 
            monitor=None)
        self.assertEqual(new_set.numrows(), 14)
        self.assertEqual(new_set.numcols(), 4)
        self.assertEqual(len(new_set), 14)
        self.assertEqual(new_set.data.shape, (14, 4))
        numpy.testing.assert_array_almost_equal(
            new_set.data.EN.values.numpy_data.tolist(), 
            [  6.49,  7.01,  7.52,  8.03,  8.54,  9.04,  
               9.55, 10.06, 10.56, 11.07, 11.57,
               12.08, 12.58, 13.09])
        numpy.testing.assert_array_almost_equal(
            new_set.data.EN.pint.to('keV').values.numpy_data.tolist(), 
            [    6490.0, 7010.0,  7520.0,  8029.999999999999,
                 8540.0, 9040.0,  9550.0,  10060.0,
                10560.0, 11070.0, 11570.0, 12080.0,
                12580.0, 13090.0])
        self.assertEqual(
            new_set.strHeader(), 
            '\n'.join([
                '#  Authors:   N, o, n, e', 
                '#  Title:     None',
                '#  Year:      None',
                '#  Institute: None',
                '#  Reference: None',
                '#  Subent:    ????????',
                '#  Reaction:  Cross section for 239Pu(n,2n)238Pu ']))
        self.assertEqual(
            new_set.reprHeader(),  
            '\n'.join([
                'Authors:   N, o, n, e',
                'Title:     None',
                'Year:      None',
                'Institute: None',
                'Reference: None',
                'Subent:    ???????? ',
                'Reaction:  (94-PU-239(N,2N)94-PU-238,SIG)',
                '']))
        self.assertEqual(str(new_set), "\n".join([
            "#  Authors:   N, o, n, e",
            "#  Title:     None",
            "#  Year:      None",
            "#  Institute: None",
            "#  Reference: None",
            "#  Subent:    ????????",
            "#  Reaction:  Cross section for 239Pu(n,2n)238Pu ",
            "#           EN    EN-ERR    DATA    DATA-ERR",
            "#          MeV       MeV      mb          mb",
            "          6.49     0.085      24          63",
            "          7.01     0.08       49          50",
            "          7.52     0.075      54          58",
            "          8.03     0.075     177          70",
            "          8.54     0.07      275          54",
            "          9.04     0.065     249          41",
            "          9.55     0.065     354          56",
            "         10.06     0.06      415          39",
            "         10.56     0.06      411          70",
            "         11.07     0.055     356          79",
            "         11.57     0.055     418          49",
            "         12.08     0.055     455          76",
            "         12.58     0.05      318         132",
            "         13.09     0.05      588         148",]))
        self.assertEqual(repr(new_set), '\n'.join([
            'Authors:   N, o, n, e',
            'Title:     None', 
            'Year:      None',
            'Institute: None', 
            'Reference: None', 
            'Subent:    ???????? ',
            'Reaction:  (94-PU-239(N,2N)94-PU-238,SIG)',
            '   EN    EN-ERR    DATA    DATA-ERR',
            '  MeV       MeV      mb          mb',
            ' 6.49     0.085      24          63',
            ' 7.01     0.08       49          50',
            ' 7.52     0.075      54          58',
            ' 8.03     0.075     177          70',
            ' 8.54     0.07      275          54',
            ' 9.04     0.065     249          41',
            ' 9.55     0.065     354          56',
            '10.06     0.06      415          39',
            '10.56     0.06      411          70',
            '11.07     0.055     356          79',
            '11.57     0.055     418          49',
            '12.08     0.055     455          76',
            '12.58     0.05      318         132',
            '13.09     0.05      588         148']))
        #self.assertEqual(new_set.getSimplified(), "")
        #self.assertTrue(False)

    def test_with_common(self):
        entry = 'O1732'
        subent = 'O1732002'
        new_set = exfor_dataset.X4DataSetNew(
            data=self.other[entry][subent]['DATA'], 
            common=self.other[entry][subent]['COMMON'])
        self.assertEqual(new_set.numrows(), 6)
        self.assertEqual(new_set.numcols(), 5)
        self.assertEqual(len(new_set), 6)
        self.assertEqual(new_set.data.shape, (6, 5))
        self.assertEqual(new_set.to_markdown(), '\n'.join([
            '  MOM (GeV/c)    COS ()    DATA (nb/sr)    ERR-S (nb/sr)    ERR-SYS (nb/sr)',
            "-------------  --------  --------------  ---------------  -----------------",
            "         2.39      0.45        0.94538          0.173479          0.0573248",
            "         2.39      0.55        0.735296         0.155972          0.044586",
            "         2.39      0.65        0.52362          0.128915          0.0318471",
            "         2.39      0.75        0.568183         0.122549          0.0342357",
            "         2.39      0.85        0.997901         0.125732          0.0613057",
            "         2.39      0.95        1.89235          0.143239          0.116242"]))

    @unittest.skip
    def test_with_pointer(self):
        pass 

    @unittest.skip
    def test_with_pointer_and_common(self):
        pass

    @unittest.skip
    def test_all(self):
        print(self.ds.keys())
        for entry in self.ds.keys():
            print(22*'=')
            print(self.ds[entry].keys())
            print([ (entry,'COMMON' in self.ds[entry][entry+'001']) for x in self.ds ])
            common = None
            for subent in self.ds[entry].keys():
                if not 'DATA' in self.ds[entry][subent]:
                    if 'COMMON' in self.ds[entry][subent]:
                        common = self.ds[entry][subent]['COMMON']
                        print("THIS GUY HAS A COMMON")
                else:
                    print("SUBENT %s" % subent)
                    new_set = exfor_dataset.X4DataSetNew(data=self.ds[entry][subent]['DATA'], common=common)
                    print(new_set.labels)
                    print(new_set.units)
                    print(new_set.data)
                    print(type(new_set.data))
                    print(new_set.data.EN.values)
                    print("size:", new_set.data.size)
                    print("shape:", new_set.data.shape)
                    print("length:", len(new_set.data))
                    print(new_set.data.EN.pint.to('keV').values)
            print()
        #print(old_set.labels)
        #print(old_set.units)
        #print(old_set.data)
        #new_set = exfor_dataset.X4DataSetNew(data=old_set.data)
        #self.assertListEqual(old_set.labels, new_set.labels)
        self.assertTrue(False)


class TestX4DataSet(TestCaseWithTableTests):

    def setUp(self):
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
