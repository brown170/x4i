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
from .utilities import TestCaseWithTableTests
import pint_pandas

testDBPath = os.path.dirname(__file__) + os.sep + 'data'
testIndexFileName = testDBPath + os.sep + 'index.tbl'
db = exfor_manager.X4DBManagerPlainFS(datapath=testDBPath, database=testIndexFileName)

class TestX4NewDataSet(TestCaseWithTableTests):

    def setUp(self):
        self.frehaut = exfor_entry.x4EntryFactory('21971', dataPath=testDBPath)
        self.other = exfor_entry.x4EntryFactory('O1732', dataPath=testDBPath)
        self.idunno = exfor_entry.x4EntryFactory('12898', filePath=os.path.dirname(__file__) + os.sep + '12898.x4')
        
    def test_easy(self):
        entry = '21971'
        subent = '21971003'
        new_set = exfor_dataset.X4DataSet(data=self.frehaut[subent]['DATA'])
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
        new_set = exfor_dataset.X4DataSet(data=self.frehaut[subent]['DATA'])
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
        self.assertEqual(new_set.to_csv(None, index=True, dequantify=False), '\n'.join([
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
        self.assertEqual(new_set.to_csv(None), '\n'.join([
            "EN,EN-ERR,DATA,DATA-ERR",
            'MeV,MeV,mb,mb',
            '6.49,0.085,24.0,63.0',
            '7.01,0.08,49.0,50.0',
            '7.52,0.075,54.0,58.0',
            '8.03,0.075,177.0,70.0',
            '8.54,0.07,275.0,54.0',
            '9.04,0.065,249.0,41.0',
            '9.55,0.065,354.0,56.0',
            '10.06,0.06,415.0,39.0',
            '10.56,0.06,411.0,70.0',
            '11.07,0.055,356.0,79.0',
            '11.57,0.055,418.0,49.0',
            '12.08,0.055,455.0,76.0',
            '12.58,0.05,318.0,132.0',
            '13.09,0.05,588.0,148.0',
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
        new_set = exfor_dataset.X4DataSet(
            data=self.frehaut[subent]['DATA'], 
            reaction=self.frehaut[subent]['BIB']['REACTION'].reactions[' '], 
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
        self.maxDiff = None
        entry = 'O1732'
        subent = 'O1732002'
        new_set = exfor_dataset.X4DataSet(
            data=self.other[subent]['DATA'], 
            common=[self.other[subent]['COMMON']])
        self.assertEqual(new_set.numrows(), 6)
        self.assertEqual(new_set.numcols(), 5)
        self.assertEqual(len(new_set), 6)
        self.assertEqual(new_set.data.shape, (6, 5))
        self.assertEqual(new_set.to_markdown(), '\n'.join([
            '  MOM (GeV/c)    COS (cosine)    DATA (nb/sr)    ERR-S (nb/sr)    ERR-SYS (nb/sr)',
            "-------------  --------------  --------------  ---------------  -----------------",
            "         2.39            0.45        0.94538          0.173479          0.0573248",
            "         2.39            0.55        0.735296         0.155972          0.044586",
            "         2.39            0.65        0.52362          0.128915          0.0318471",
            "         2.39            0.75        0.568183         0.122549          0.0342357",
            "         2.39            0.85        0.997901         0.125732          0.0613057",
            "         2.39            0.95        1.89235          0.143239          0.116242"]))
        self.maxDiff=None
        # While we're at it, let's test unit conversion!
        new_set.data["MOM"] = new_set.data["MOM"].pint.to("MeV/c")
        self.assertEqual(new_set.to_markdown(), '\n'.join([
            '  MOM (MeV/c)    COS (cosine)    DATA (nb/sr)    ERR-S (nb/sr)    ERR-SYS (nb/sr)',
            "-------------  --------------  --------------  ---------------  -----------------",
            "         2390            0.45        0.94538          0.173479          0.0573248",
            "         2390            0.55        0.735296         0.155972          0.044586",
            "         2390            0.65        0.52362          0.128915          0.0318471",
            "         2390            0.75        0.568183         0.122549          0.0342357",
            "         2390            0.85        0.997901         0.125732          0.0613057",
            "         2390            0.95        1.89235          0.143239          0.116242"]))

    def test_with_pointer(self):
        entry = '12898'
        subent = '12898002'
        new_set = exfor_dataset.X4DataSet(
            data=self.idunno[subent]['DATA'], 
            pointer='2')
        self.assertEqual(new_set.to_markdown(), '\n'.join([
            '  EN (MeV)    EN-RSL-FW (MeV)    ERR-S (%)    MONIT (mb)    MONIT-ERR (%)    DATA (mb)    ERR-T (%)',
            '----------  -----------------  -----------  ------------  ---------------  -----------  -----------',
            '     2.856              0.095         47.9         528.8              3       0.004799         50.5',
            '     2.957              0.094         20.6         524.4              3       0.01031          22.8',
            '     3.057              0.094         15.9         522.7              2.5     0.01346          25.7',
            '     3.158              0.092          6.7         524.2              2.5     0.03863          17.1',
            '     3.258              0.09           4.9         526.7              2.5     0.07588          12.5',
            '     3.359              0.087          3.6         529.2              2.5     0.1246            9.2',
            '     3.459              0.087          3.4         531.7              2.5     0.1707            7.9',
            '     3.56               0.087          3.2         536.1              2.5     0.2214            8.8',
            '     3.661              0.087          3           541.7              2.5     0.3326            8.2',
            '     3.761              0.082          2.9         544.3              2.5     0.4309            9.2',
            '     3.861              0.084          2.8         544.9              2.5     0.6979            7',
            '     3.861              0.084          2.8         544.9              2.5     0.6986            7',
            '     3.962              0.081          2.8         545.5              2.5     0.7353            6.1',
            '     4.063              0.081          2.8         546.3              2.4     0.8476            6.3',
            '     4.264              0.075          2.7         547.4              2.4     1.007             7.6',
            '     4.464              0.076          2.7         549                2.4     1.478             6.4',
            '     4.664              0.076          2.8         544                2.4     2.25              6',
            '     4.865              0.076          2.8         537.6              2.4     2.686             6.1',
        ]))

    def test_with_pointer_and_transform(self):
        entry = '12898'
        subent = '12898002'
        new_set = exfor_dataset.X4DataSet(
            data=self.idunno[subent]['DATA'], 
            pointer='2')
        new_set.data["ERR-T"] = (new_set.data["DATA"] * new_set.data["ERR-T"]).pint.to("mb")
        self.maxDiff = None
        self.assertEqual(new_set.to_markdown(), '\n'.join([
            '  EN (MeV)    EN-RSL-FW (MeV)    ERR-S (%)    MONIT (mb)    MONIT-ERR (%)    DATA (mb)    ERR-T (mb)',
            '----------  -----------------  -----------  ------------  ---------------  -----------  ------------',
            '     2.856              0.095         47.9         528.8              3       0.004799    0.0024235',
            '     2.957              0.094         20.6         524.4              3       0.01031     0.00235068',
            '     3.057              0.094         15.9         522.7              2.5     0.01346     0.00345922',
            '     3.158              0.092          6.7         524.2              2.5     0.03863     0.00660573',
            '     3.258              0.09           4.9         526.7              2.5     0.07588     0.009485',
            '     3.359              0.087          3.6         529.2              2.5     0.1246      0.0114632',
            '     3.459              0.087          3.4         531.7              2.5     0.1707      0.0134853',
            '     3.56               0.087          3.2         536.1              2.5     0.2214      0.0194832',
            '     3.661              0.087          3           541.7              2.5     0.3326      0.0272732',
            '     3.761              0.082          2.9         544.3              2.5     0.4309      0.0396428',
            '     3.861              0.084          2.8         544.9              2.5     0.6979      0.048853',
            '     3.861              0.084          2.8         544.9              2.5     0.6986      0.048902',
            '     3.962              0.081          2.8         545.5              2.5     0.7353      0.0448533',
            '     4.063              0.081          2.8         546.3              2.4     0.8476      0.0533988',
            '     4.264              0.075          2.7         547.4              2.4     1.007       0.076532',
            '     4.464              0.076          2.7         549                2.4     1.478       0.094592',
            '     4.664              0.076          2.8         544                2.4     2.25        0.135',
            '     4.865              0.076          2.8         537.6              2.4     2.686       0.163846',
        ]))

    def test_with_pointer_and_common(self):
        entry = '12898'
        subent = '12898002'
        new_set = exfor_dataset.X4DataSet(
            data=self.idunno[subent]['DATA'], 
            common=[self.other['O1732002']['COMMON']],  # fake common
            pointer='2')
        # print(new_set.to_markdown())
        self.assertEqual(new_set.to_markdown(), '\n'.join([
            '  MOM (GeV/c)    EN (MeV)    EN-RSL-FW (MeV)    ERR-S (%)    MONIT (mb)    MONIT-ERR (%)    DATA (mb)    ERR-T (%)',
            '-------------  ----------  -----------------  -----------  ------------  ---------------  -----------  -----------',
            '         2.39       2.856              0.095         47.9         528.8              3       0.004799         50.5',
            '         2.39       2.957              0.094         20.6         524.4              3       0.01031          22.8',
            '         2.39       3.057              0.094         15.9         522.7              2.5     0.01346          25.7',
            '         2.39       3.158              0.092          6.7         524.2              2.5     0.03863          17.1',
            '         2.39       3.258              0.09           4.9         526.7              2.5     0.07588          12.5',
            '         2.39       3.359              0.087          3.6         529.2              2.5     0.1246            9.2',
            '         2.39       3.459              0.087          3.4         531.7              2.5     0.1707            7.9',
            '         2.39       3.56               0.087          3.2         536.1              2.5     0.2214            8.8',
            '         2.39       3.661              0.087          3           541.7              2.5     0.3326            8.2',
            '         2.39       3.761              0.082          2.9         544.3              2.5     0.4309            9.2',
            '         2.39       3.861              0.084          2.8         544.9              2.5     0.6979            7',
            '         2.39       3.861              0.084          2.8         544.9              2.5     0.6986            7',
            '         2.39       3.962              0.081          2.8         545.5              2.5     0.7353            6.1',
            '         2.39       4.063              0.081          2.8         546.3              2.4     0.8476            6.3',
            '         2.39       4.264              0.075          2.7         547.4              2.4     1.007             7.6',
            '         2.39       4.464              0.076          2.7         549                2.4     1.478             6.4',
            '         2.39       4.664              0.076          2.8         544                2.4     2.25              6',
            '         2.39       4.865              0.076          2.8         537.6              2.4     2.686             6.1',
        ]))


if __name__ == "__main__":
    # try:
    #     import xmlrunner
    #     unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-results'))
    # except ImportError:
    unittest.main()
    print()
    print()
