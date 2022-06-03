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
#   1.     improve readability (David Brown <dbrown@bnl.gov>, 2018-12-06T00:19:18)
#   2.     no xmlrunner for now (David Brown <dbrown@bnl.gov>, 2018-12-04T22:06:10)
#   3.     from __future__ imports missing (David Brown <dbrown@bnl.gov>, 2018-12-04T18:36:38)
#   4.     Python3.X compatibility & PEP-8 compliance (David Brown <dbrown@bnl.gov>, 2018-12-04T15:18:59)
#   5.     tweak paths again (David Brown <dbrown@bnl.gov>, 2014-09-15T14:25:41)
#   6.     tweak test data paths (David Brown <dbrown@bnl.gov>, 2014-09-15T14:19:36)
#   7.     fix whitespace in a few unit tests & fix call to retrieve (David Brown <dbrown@bnl.gov>, 2014-02-13T15:57:05)
#   8.     small database for unit testing (David Brown <dbrown@bnl.gov>, 2014-02-04T17:31:06)
#   9.     add optional call to XML test runner (David Brown <dbrown@bnl.gov>, 2012-01-23T19:09:00)
#
################################################################################

from __future__ import print_function, division

import os
import unittest

# Set up the paths to x4i & friends
from x4i import exfor_entry
from x4i import exfor_manager
from x4i.test import __path__
from x4i.test.utilities import TestCaseWithTableTests

testDBPath = __path__[0] + os.sep + 'data'
testIndexFileName = testDBPath + os.sep + 'index.tbl'

NEWENTRYANSWER = {'E0783': [
    '''SUBENT        E0783001   20040622              20050926       0000
BIB                 10         19
TITLE       ACCELERATION OF PROTONS AND DEUTERONS POLARIZED IN
            THE HORIZONTAL PLANEBY THE RCNP CYCLOTRON
AUTHOR     (K.HATANAKA,N.MATSUOKA,H.SAKAI,T.SAITO,H.TAMURA,
           K.HOSONO,M.KONDO,K.IMAI,H.SHIMIZU,K.NISHIMURA)
INSTITUTE  (2JPNOSA) RESEARCH CENTER FOR NUCLEAR PHYSICS, OSAKA
            UNIV.
           (2JPNKTO)
REFERENCE  (J,NIM,217,397,1983)
FACILITY   (CYCLO,2JPNOSA)
INC-SOURCE  BEAM-INTENSITY IS 0.5NA
            BEAM-POLARIZATION IS NOT GIVEN
           (ATOMI) with a Wien filter
SAMPLE      TARGET IS NOT POLARIZED
            TARGET IS NOT ALIGNED
PART-DET   (D)
STATUS     (CURVE) DATA TAKEN FROM GRAPH
HISTORY    (19881027T) CONVERTED FROM NRDF DATA NO. D783
           (20040401A) Author's name is corrected. Code is added
                       into INC-SOURCE. E-EXC=0.0 MeV is deleted.
ENDBIB              19
COMMON               1          3
EN
MEV
56.
ENDCOMMON            3
ENDSUBENT           26
''', '''SUBENT        E0783002   20040622              20050926       0000
BIB                  4          5
REACTION   (1-H-1(D,EL)1-H-1,SL,POL/DA,,ANA)
FLAG       (1.) DATA ERROR IS SMALLER THAN DATA POINT
ERR-ANALYS (DATA-ERR) Uncertainty scanned from figure
HISTORY    (20040401A) Quantity code is correcetd.
                       ERR-ANALYS is added.
ENDBIB               5
NOCOMMON             0          0
DATA                 4         24
ANG-CM     DATA       DATA-ERR   FLAG
ADEG       NO-DIM     NO-DIM     NO-DIM
     30.712 -2.211E-03                    1.
     38.727 -5.861E-03  0.821E-02
     46.135  1.022E-02                    1.
     55.814  4.098E-02                    1.
     64.866  7.998E-02                    1.
     69.415  1.126E-01                    1.
     74.316  1.633E-01  0.147E-01
     79.924  2.517E-01  0.115E-01
     84.442  2.663E-01  0.131E-01
     89.661  3.153E-01  0.821E-02
     94.181  3.315E-01  0.164E-01
     99.114  4.003E-01  0.115E-01
    104.318  4.411E-01  0.131E-01
    109.841  4.802E-01  0.132E-01
    115.135  3.880E-01  0.132E-01
    120.355  2.531E-01  0.131E-01
    125.595 -5.416E-02  0.214E-01
    129.340 -2.990E-01  0.197E-01
    134.447 -3.140E-01  0.180E-01
    139.629 -1.024E-01  0.197E-01
    145.538 -2.551E-02  0.148E-01
    150.255  1.040E-01  0.246E-01
    155.357  8.570E-02  0.246E-01
    160.562  1.265E-01  0.197E-01
ENDDATA             26
ENDSUBENT           36
''']}


class TestTheWorks(TestCaseWithTableTests):
    def setUp(self):
        self.dbMgr = exfor_manager.X4DBManagerPlainFS(datapath=testDBPath, database=testIndexFileName)

    def test_polarization(self):
        self.maxDiff = None
        # Get the subentry (formatted as a full entry)
        subent = self.dbMgr.retrieve(SUBENT='E0783002', rawEntry=True)
        self.assertEqual(subent, {'E0783': [NEWENTRYANSWER['E0783'][0], NEWENTRYANSWER['E0783'][1]]})
        # Translate the subentry & extract the datasets
        ds = exfor_entry.X4Entry(subent['E0783']).getDataSets()
        # Check a prototypical one
        self.assertTablesAlmostEqual(str(ds[('E0783', 'E0783002', ' ')]),
                                     '#  Authors:   K.Hatanaka, N.Matsuoka, H.Sakai, T.Saito, H.Tamura, K.Hosono, M.Kondo, K.Imai, H.Shimizu, K.Nishimura\n'
                                     '#  Title:     Acceleration Of Protons And Deuterons Polarized In The Horizontal Planeby The Rcnp Cyclotron\n'
                                     '#  Year:      1983\n'
                                     '#  Institute: Osaka Univ., Osaka (Research Center For Nuclear Physics, Osaka Univ.); Kyoto Univ.\n'
                                     '#  Reference: Nuclear Instrum.and Methods in Physics Res. 217, 397 (1983)\n'
                                     '#  Subent:    E0783002\n'
                                     '#  Reaction:  Vector analyzing power, A(y), for incident beam Spin-polarization probability d/dA for 1H(d,Elastic)1H \n'
                                     '#        EN            ANG-CM        DATA          DATA-ERR      FLAG          \n'
                                     '#        MEV           ADEG          NO-DIM        NO-DIM        NO-DIM        \n'
                                     '        56.0          30.712        -0.002211     None          1.0           \n'
                                     '        56.0          38.727        -0.005861     0.00821       None          \n'
                                     '        56.0          46.135        0.01022       None          1.0           \n'
                                     '        56.0          55.814        0.04098       None          1.0           \n'
                                     '        56.0          64.866        0.07998       None          1.0           \n'
                                     '        56.0          69.415        0.1126        None          1.0           \n'
                                     '        56.0          74.316        0.1633        0.0147        None          \n'
                                     '        56.0          79.924        0.2517        0.0115        None          \n'
                                     '        56.0          84.442        0.2663        0.0131        None          \n'
                                     '        56.0          89.661        0.3153        0.00821       None          \n'
                                     '        56.0          94.181        0.3315        0.0164        None          \n'
                                     '        56.0          99.114        0.4003        0.0115        None          \n'
                                     '        56.0          104.318       0.4411        0.0131        None          \n'
                                     '        56.0          109.841       0.4802        0.0132        None          \n'
                                     '        56.0          115.135       0.388         0.0132        None          \n'
                                     '        56.0          120.355       0.2531        0.0131        None          \n'
                                     '        56.0          125.595       -0.05416      0.0214        None          \n'
                                     '        56.0          129.34        -0.299        0.0197        None          \n'
                                     '        56.0          134.447       -0.314        0.018         None          \n'
                                     '        56.0          139.629       -0.1024       0.0197        None          \n'
                                     '        56.0          145.538       -0.02551      0.0148        None          \n'
                                     '        56.0          150.255       0.104         0.0246        None          \n'
                                     '        56.0          155.357       0.0857        0.0246        None          \n'
                                     '        56.0          160.562       0.1265        0.0197        None          \n        ')

    def test_cs_Pun2n(self):
        # Get all the data
        subents = self.dbMgr.retrieve(target="PU-239", reaction="N,2N", quantity="CS", rawEntry=True)
        # Lougheed dataset
        ds = exfor_entry.X4Entry(subents['13883']).getSimplifiedDataSets()
        self.assertTablesAlmostEqual(str(ds[('13883', '13883002', ' ')]).strip(), '''
#  Authors:   R.W.Lougheed, W.Webster, M.N.Namboodiri, D.R.Nethaway, K.J.Moody, J.H.Landrum, R.W.Hoff, R.J.Dupzyk, J.H.Mcquaid, R.Gunnink, E.D.Watkins
#  Title:     239Pu And 241Am(N,2N) Cross-Section Measurements Near E(N) = 14 Mev
#  Year:      2002
#  Institute: Lawrence Livermore National Laboratory, Livermore, CA
#  Reference: Radiochimica Acta 90, 833 (2002)
#  Subent:    13883002
#  Reaction:  Cross section for 239Pu(n,2n)238Pu
#  Monitor(s): ((79-AU-197(N,2N)79-AU-196,SIG), 'Flux monitor. Neutron energy determined using 54Fe(n,p) reaction.', None)
#        Energy        Data          d(Data)
#        MeV           barns         barns
        13.8          0.228         0.006384
        14.0          0.219         0.007884
        14.8          0.214         0.002996'''.strip())
        # Frehaut dataset
        ds = exfor_entry.X4Entry(subents['21971']).getSimplifiedDataSets()
        self.assertTablesAlmostEqual(str(ds[('21971', '21971003', ' ')]).strip(), '''
#  Authors:   J.Frehaut, A.Bertin, R.Blois, E.Gryntakis, C.A.Philis
#  Title:     -(N,2N) Cross Sections Of 2-H And 239-Pu
#  Year:      1985\n#  Institute: 2FR
#  Reference: Conf.on Nucl.Data f.Basic a.Appl.Sci.,Santa Fe 1985 , (IB06) (1985)
#  Subent:    21971003
#  Reaction:  Cross section for 239Pu(n,2n)238Pu
#        Energy        Data          d(Energy)     d(Data)
#        MeV           barns         MeV           barns
        6.49          0.024         0.085         0.063
        7.01          0.049         0.08          0.05
        7.52          0.054         0.075         0.058
        8.03          0.177         0.075         0.07
        8.54          0.275         0.07          0.054
        9.04          0.249         0.065         0.041
        9.55          0.354         0.065         0.056
        10.06         0.415         0.06          0.039
        10.56         0.411         0.06          0.07
        11.07         0.356         0.055         0.079
        11.57         0.418         0.055         0.049
        12.08         0.455         0.055         0.076
        12.58         0.318         0.05          0.132
        13.09         0.588         0.05          0.148'''.strip())
        # Mather datasets
        ds = exfor_entry.X4Entry(subents['20795']).getSimplifiedDataSets()
        self.assertTablesAlmostEqual(str(ds[('20795', '20795014', ' ')]).strip(), '''
#  Authors:   D.S.Mather, P.F.Bampton, R.E.Coles, G.James, P.J.Nind
#  Title:     -Measurement Of (N,2N) Cross Sections For Incident Energies Between 6 And 14 Mev-.
#  Year:      1972
#  Institute: 2UK
#  Reference: Report other than progress report: AWRE-O-72/72  (1972); Report other than progress report: AWRE-O-47/69  (1969)
#  Subent:    20795014
#  Reaction:  Cross section for 239Pu(n,2n)238Pu
#  Monitor(s): ((94-PU-239(N,F),SIG), '1917MB+-8PERCENT  AT 6.5MEV 2030MB+-8.5PERCENT AT 7.1MEV 2213MB+-9PERCENT   AT 8.0MEV 2252MB+-9.5PERCENT AT 9.0MEV', None)
#        Energy        Data          d(Data)
#        MeV           barns         barns
        6.5           0.419         0.053
        7.1           0.451         0.06
        8.0           0.49          0.057
        9.0           0.51          0.09          '''.strip())
        # GEANIE dataset
        ds = exfor_entry.X4Entry(subents['14129']).getSimplifiedDataSets()
        self.assertTablesAlmostEqual(str(ds[('14129', '14129002', ' ')]).strip(), '''
#  Authors:   J.A.Becker, L.A.Bernstein, W.Younes, D.P.Mcnabb, P.E.Garrett, D.E.Archer, C.A.Mcgrath, M.A.Stoyer, H.Chen, W.E.Ormand, R.O.Nelson, M.B.Chadwick, G.D.Johns, D.Drake, P.G.Young, M.Devlin, N.Fotiades, W.S.Wilburn
#  Title:     Partial Gamma-Ray Cross Sections For The Reaction 239Pu(N,2Ng) And The 239Pu(N,2N) Cross Section
#  Year:      2002
#  Institute: Lawrence Livermore National Laboratory, Livermore, CA
#  Reference: J.Nucl.Science and Technol.Tokyo,Supplement 2, (1), 620 (2002)
#  Subent:    14129002
#  Reaction:  Cross section for 239Pu(n,2n)238Pu
#        Energy        Data          d(Energy)     d(Data)
#        MeV           barns         MeV           barns
        6.481         0.1009        0.2239        0.03081
        6.942         0.1261        0.1894        0.02015
        7.49          0.1525        0.2412        0.01422
        8.084         0.2263        0.2582        0.0154
        8.751         0.2669        0.293         0.01659
        9.504         0.3029        0.3446        0.01659
        10.34         0.3508        0.3961        0.02014
        11.34         0.3561        0.4307        0.02015
        12.45         0.2951        0.534         0.01776
        13.77         0.2284        0.603         0.01539
        15.33         0.1558        0.7231        0.0154
        17.19         0.1178        0.8438        0.008262
        19.34         0.1025        1.068         0.007097
        '''.strip())

    def test_angular_dist(self):
        subent = self.dbMgr.retrieve(SUBENT='11321004', rawEntry=True)
        ds = exfor_entry.X4Entry(subent['11321']).getDataSets()
        # open( 'a', mode = 'w' ).writelines( str( ds[ ('11321', '11321004', ' ') ] ) )
        self.assertTablesAlmostEqual(str(ds[('11321', '11321004', ' ')]),
                                     '#  Authors:   R.W.Hill\n'
                                     '#  Title:     Angular Distributions Of Elastic Scattering Of 5-Mev Neutrons.\n'
                                     '#  Year:      1958\n#  Institute: Westinghouse Research Lab., Pittsburgh, PA\n'
                                     '#  Reference: Physical Review 109, 2105 (1958)\n#  Subent:    11321004\n'
                                     '#  Reaction:  Differential c/s with respect to angle for 27Al(n,Elastic)27Al \n'
                                     '#  Frame:     Lab\n'
                                     '#        EN            EN-RSL        ANG-RSL       COS           DATA          DATA-ERR      \n'
                                     '#        MEV           MEV           ADEG          NO-DIM        MB/SR         MB/SR         \n'
                                     '        5.0           0.1           10.0          0.866         290.0         30.0          \n'
                                     '        5.0           0.1           10.0          0.766         212.0         10.0          \n'
                                     '        5.0           0.1           10.0          0.643         140.0         10.0          \n'
                                     '        5.0           0.1           10.0          0.5           70.0          9.0           \n'
                                     '        5.0           0.1           10.0          0.342         43.0          6.0           \n'
                                     '        5.0           0.1           10.0          0.174         40.0          5.0           \n'
                                     '        5.0           0.1           10.0          0.0           30.0          3.0           \n'
                                     '        5.0           0.1           10.0          -0.174        30.0          5.0           \n'
                                     '        5.0           0.1           10.0          -0.342        25.0          4.0           \n'
                                     '        5.0           0.1           10.0          -0.5          20.0          5.0           \n'
                                     '        5.0           0.1           10.0          -0.643        22.0          5.0           \n'
                                     '        5.0           0.1           10.0          -0.766        22.0          4.0           \n'
                                     '        5.0           0.1           10.0          -0.866        25.0          4.0           \n        ')
        simple = ds[('11321', '11321004', ' ')].getSimplified()
        # open( 'b', mode = 'w' ).writelines( str( simple ) )
        self.assertTablesAlmostEqual(str(simple),
                                     '#  Authors:   R.W.Hill\n'
                                     '#  Title:     Angular Distributions Of Elastic Scattering Of 5-Mev Neutrons.\n'
                                     '#  Year:      1958\n#  Institute: Westinghouse Research Lab., Pittsburgh, PA\n'
                                     '#  Reference: Physical Review 109, 2105 (1958)\n#  Subent:    11321004\n'
                                     '#  Reaction:  Differential c/s with respect to angle for 27Al(n,Elastic)27Al \n'
                                     '#  Frame:     Lab\n'
                                     '#        Energy        Angle         Data          d(Energy)     d(Angle)      d(Data)       \n'
                                     '#        MeV           degrees       barns/ster    MeV           degrees       barns/ster    \n'
                                     '        5.0           30.0029109312 0.29          0.05          5.0           0.03          \n'
                                     '        5.0           40.0039613369 0.212         0.05          5.0           0.01          \n'
                                     '        5.0           49.9841125607 0.14          0.05          5.0           0.01          \n'
                                     '        5.0           60.0          0.07          0.05          5.0           0.009         \n'
                                     '        5.0           70.0012281921 0.043         0.05          5.0           0.006         \n'
                                     '        5.0           79.9795304514 0.04          0.05          5.0           0.005         \n'
                                     '        5.0           90.0          0.03          0.05          5.0           0.003         \n'
                                     '        5.0           100.020469549 0.03          0.05          5.0           0.005         \n'
                                     '        5.0           109.998771808 0.025         0.05          5.0           0.004         \n'
                                     '        5.0           120.0         0.02          0.05          5.0           0.005         \n'
                                     '        5.0           130.015887439 0.022         0.05          5.0           0.005         \n'
                                     '        5.0           139.996038663 0.022         0.05          5.0           0.004         \n'
                                     '        5.0           149.997089069 0.025         0.05          5.0           0.004         \n        ')

    def test_angular_dist_cm(self):
        subent = self.dbMgr.retrieve(SUBENT='11314002', rawEntry=True)
        ds = exfor_entry.X4Entry(subent['11314']).getDataSets()
        # open( 'c', mode = 'w' ).writelines( str( ds[ ('11314', '11314002', ' ') ] ) )
        self.assertTablesAlmostEqual(str(ds[('11314', '11314002', ' ')]),
                                     '#  Authors:   J.L.Fowler, C.H.Johnson\n'
                                     '#  Title:     Differential Elastic Scattering Cross Sections For Neutrons On Nitrogen.\n'
                                     '#  Year:      1955\n#  Institute: Oak Ridge National Laboratory, Oak Ridge, TN\n'
                                     '#  Reference: Physical Review 98, 728 (1955)\n#  Subent:    11314002\n'
                                     '#  Reaction:  Differential c/s with respect to angle for 14N(n,Elastic)14N \n'
                                     '#  Frame:     Center of mass\n'
                                     '#        EN            EN-RSL        COS-CM        DATA-CM       \n'
                                     '#        MEV           MEV           NO-DIM        MB/SR         \n'
                                     '        0.8           0.05          0.85          164.0         \n'
                                     '        0.8           0.05          0.65          170.0         \n'
                                     '        0.8           0.05          0.46          157.0         \n'
                                     '        0.8           0.05          0.27          167.0         \n'
                                     '        0.8           0.05          0.07          151.0         \n'
                                     '        0.8           0.05          -0.11         156.0         \n'
                                     '        0.8           0.05          -0.31         165.0         \n'
                                     '        0.8           0.05          -0.51         143.0         \n'
                                     '        0.8           0.05          -0.7          128.0         \n'
                                     '        0.97          0.02          0.49          90.0          \n'
                                     '        0.97          0.02          0.45          88.0          \n'
                                     '        0.97          0.02          0.42          83.0          \n'
                                     '        0.97          0.02          0.39          76.0          \n'
                                     '        0.97          0.02          0.36          76.0          \n'
                                     '        0.97          0.02          0.31          76.0          \n'
                                     '        0.97          0.02          0.28          80.0          \n'
                                     '        0.97          0.02          0.24          83.0          \n'
                                     '        0.97          0.02          0.2           82.0          \n'
                                     '        0.97          0.02          0.17          78.0          \n'
                                     '        0.97          0.02          0.14          78.0          \n'
                                     '        0.97          0.02          0.1           75.0          \n'
                                     '        0.97          0.02          0.06          76.0          \n'
                                     '        0.97          0.02          0.02          78.0          \n'
                                     '        0.97          0.02          -0.01         80.0          \n'
                                     '        0.97          0.02          -0.04         80.0          \n'
                                     '        0.97          0.02          -0.08         73.0          \n'
                                     '        0.97          0.02          -0.12         78.0          \n'
                                     '        0.97          0.02          -0.16         80.0          \n'
                                     '        0.97          0.02          -0.19         70.0          \n'
                                     '        0.97          0.02          -0.22         76.0          \n'
                                     '        0.97          0.02          -0.26         76.0          \n'
                                     '        0.97          0.02          -0.3          74.0          \n'
                                     '        0.97          0.02          -0.34         73.0          \n'
                                     '        0.97          0.02          -0.38         73.0          \n'
                                     '        0.97          0.02          -0.41         70.0          \n'
                                     '        0.97          0.02          -0.46         70.0          \n'
                                     '        0.97          0.02          -0.49         66.0          \n'
                                     '        0.97          0.02          -0.52         70.0          \n'
                                     '        0.97          0.02          -0.54         65.0          \n'
                                     '        0.97          0.02          -0.59         65.0          \n'
                                     '        0.97          0.02          -0.62         70.0          \n'
                                     '        0.97          0.02          -0.65         60.0          \n'
                                     '        0.97          0.02          -0.68         70.0          \n'
                                     '        0.97          0.02          -0.74         65.0          \n'
                                     '        0.97          0.02          -0.76         65.0          \n'
                                     '        0.97          0.02          -0.8          60.0          \n'
                                     '        0.97          0.02          -0.84         63.0          \n'
                                     '        0.97          0.02          -0.88         60.0          \n'
                                     '        0.97          0.02          -0.91         55.0          \n'
                                     '        0.97          0.02          -0.94         45.0          \n'
                                     '        0.97          0.02          -0.98         40.0          \n'
                                     '        1.082         0.01          0.47          148.0         \n'
                                     '        1.082         0.01          0.41          135.0         \n'
                                     '        1.082         0.01          0.34          145.0         \n'
                                     '        1.082         0.01          0.28          133.0         \n'
                                     '        1.082         0.01          0.21          126.0         \n'
                                     '        1.082         0.01          0.15          125.0         \n'
                                     '        1.082         0.01          0.1           135.0         \n'
                                     '        1.082         0.01          0.02          145.0         \n'
                                     '        1.082         0.01          -0.04         140.0         \n'
                                     '        1.082         0.01          -0.11         130.0         \n'
                                     '        1.082         0.01          -0.18         130.0         \n'
                                     '        1.082         0.01          -0.23         147.0         \n'
                                     '        1.082         0.01          -0.3          139.0         \n'
                                     '        1.082         0.01          -0.36         138.0         \n'
                                     '        1.082         0.01          -0.43         143.0         \n'
                                     '        1.082         0.01          -0.5          142.0         \n'
                                     '        1.082         0.01          -0.55         140.0         \n'
                                     '        1.082         0.01          -0.62         143.0         \n'
                                     '        1.082         0.01          -0.68         140.0         \n'
                                     '        1.082         0.01          -0.76         145.0         \n'
                                     '        1.082         0.01          -0.81         130.0         \n'
                                     '        1.082         0.01          -0.88         117.0         \n'
                                     '        1.082         0.01          -0.94         110.0         \n'
                                     '        1.11          0.01          0.47          214.0         \n'
                                     '        1.11          0.01          0.42          204.0         \n'
                                     '        1.11          0.01          0.36          194.0         \n'
                                     '        1.11          0.01          0.3           186.0         \n'
                                     '        1.11          0.01          0.23          182.0         \n'
                                     '        1.11          0.01          0.17          180.0         \n'
                                     '        1.11          0.01          0.12          178.0         \n'
                                     '        1.11          0.01          0.05          172.0         \n'
                                     '        1.11          0.01          -0.02         169.0         \n'
                                     '        1.11          0.01          -0.07         174.0         \n'
                                     '        1.11          0.01          -0.14         168.0         \n'
                                     '        1.11          0.01          -0.2          170.0         \n'
                                     '        1.11          0.01          -0.26         178.0         \n'
                                     '        1.11          0.01          -0.32         178.0         \n'
                                     '        1.11          0.01          -0.39         187.0         \n'
                                     '        1.11          0.01          -0.44         195.0         \n'
                                     '        1.11          0.01          -0.5          190.0         \n'
                                     '        1.11          0.01          -0.56         195.0         \n'
                                     '        1.11          0.01          -0.63         202.0         \n'
                                     '        1.11          0.01          -0.69         185.0         \n'
                                     '        1.11          0.01          -0.76         207.0         \n'
                                     '        1.11          0.01          -0.81         185.0         \n'
                                     '        1.12          0.01          0.47          315.0         \n'
                                     '        1.12          0.01          0.43          270.0         \n'
                                     '        1.12          0.01          0.37          220.0         \n'
                                     '        1.12          0.01          0.3           230.0         \n'
                                     '        1.12          0.01          0.23          220.0         \n'
                                     '        1.12          0.01          0.18          205.0         \n'
                                     '        1.12          0.01          0.12          190.0         \n'
                                     '        1.12          0.01          0.06          215.0         \n'
                                     '        1.12          0.01          0.0           185.0         \n'
                                     '        1.12          0.01          -0.06         195.0         \n'
                                     '        1.12          0.01          -0.12         185.0         \n'
                                     '        1.12          0.01          -0.18         175.0         \n'
                                     '        1.12          0.01          -0.23         175.0         \n'
                                     '        1.12          0.01          -0.3          175.0         \n'
                                     '        1.12          0.01          -0.37         180.0         \n'
                                     '        1.12          0.01          -0.43         175.0         \n'
                                     '        1.12          0.01          -0.47         180.0         \n'
                                     '        1.12          0.01          -0.54         170.0         \n'
                                     '        1.12          0.01          -0.6          190.0         \n'
                                     '        1.12          0.01          -0.66         175.0         \n'
                                     '        1.12          0.01          -0.73         185.0         \n'
                                     '        1.12          0.01          -0.8          180.0         \n'
                                     '        1.12          0.01          -0.86         170.0         \n'
                                     '        1.12          0.01          -0.9          145.0         \n'
                                     '        1.12          0.01          -0.98         130.0         \n'
                                     '        1.13          0.01          0.48          260.0         \n'
                                     '        1.13          0.01          0.42          240.0         \n'
                                     '        1.13          0.01          0.36          207.0         \n'
                                     '        1.13          0.01          0.3           198.0         \n'
                                     '        1.13          0.01          0.25          202.0         \n'
                                     '        1.13          0.01          0.18          182.0         \n'
                                     '        1.13          0.01          0.12          171.0         \n'
                                     '        1.13          0.01          0.05          172.0         \n'
                                     '        1.13          0.01          0.0           155.0         \n'
                                     '        1.13          0.01          -0.06         165.0         \n'
                                     '        1.13          0.01          -0.12         156.0         \n'
                                     '        1.13          0.01          -0.2          142.0         \n'
                                     '        1.13          0.01          -0.25         134.0         \n'
                                     '        1.13          0.01          -0.32         140.0         \n'
                                     '        1.13          0.01          -0.37         130.0         \n'
                                     '        1.13          0.01          -0.44         124.0         \n'
                                     '        1.13          0.01          -0.51         133.0         \n'
                                     '        1.13          0.01          -0.56         133.0         \n'
                                     '        1.13          0.01          -0.62         129.0         \n'
                                     '        1.13          0.01          -0.68         119.0         \n'
                                     '        1.13          0.01          -0.74         140.0         \n'
                                     '        1.13          0.01          -0.8          121.0         \n'
                                     '        1.13          0.01          -0.86         128.0         \n'
                                     '        1.13          0.01          -0.92         114.0         \n'
                                     '        1.16          0.01          0.45          132.0         \n'
                                     '        1.16          0.01          0.385         135.0         \n'
                                     '        1.16          0.01          0.33          127.0         \n'
                                     '        1.16          0.01          0.27          117.0         \n'
                                     '        1.16          0.01          0.2           116.0         \n'
                                     '        1.16          0.01          0.15          120.0         \n'
                                     '        1.16          0.01          0.08          125.0         \n'
                                     '        1.16          0.01          0.04          110.0         \n'
                                     '        1.16          0.01          -0.03         100.0         \n'
                                     '        1.16          0.01          -0.07         105.0         \n'
                                     '        1.16          0.01          -0.14         95.0          \n'
                                     '        1.16          0.01          -0.2          105.0         \n'
                                     '        1.16          0.01          -0.26         99.0          \n'
                                     '        1.16          0.01          -0.32         110.0         \n'
                                     '        1.16          0.01          -0.38         100.0         \n'
                                     '        1.16          0.01          -0.43         110.0         \n'
                                     '        1.16          0.01          -0.5          99.0          \n'
                                     '        1.16          0.01          -0.55         105.0         \n'
                                     '        1.16          0.01          -0.62         105.0         \n'
                                     '        1.16          0.01          -0.67         99.0          \n'
                                     '        1.16          0.01          -0.73         102.0         \n'
                                     '        1.16          0.01          -0.78         105.0         \n'
                                     '        1.16          0.01          -0.84         98.0          \n'
                                     '        1.16          0.01          -0.9          90.0          \n'
                                     '        1.16          0.01          -0.96         67.0          \n'
                                     '        1.35          0.02          0.52          215.0         \n'
                                     '        1.35          0.02          0.41          224.0         \n'
                                     '        1.35          0.02          0.33          185.0         \n'
                                     '        1.35          0.02          0.23          180.0         \n'
                                     '        1.35          0.02          0.14          180.0         \n'
                                     '        1.35          0.02          0.05          170.0         \n'
                                     '        1.35          0.02          -0.04         163.0         \n'
                                     '        1.35          0.02          -0.13         180.0         \n'
                                     '        1.35          0.02          -0.22         168.0         \n'
                                     '        1.35          0.02          -0.33         179.0         \n'
                                     '        1.35          0.02          -0.39         193.0         \n'
                                     '        1.35          0.02          -0.47         187.0         \n'
                                     '        1.35          0.02          -0.57         203.0         \n'
                                     '        1.35          0.02          -0.65         210.0         \n'
                                     '        1.35          0.02          -0.73         218.0         \n'
                                     '        1.35          0.02          -0.81         227.0         \n'
                                     '        1.35          0.02          -0.92         233.0         \n'
                                     '        1.377         0.02          0.53          210.0         \n'
                                     '        1.377         0.02          0.43          192.0         \n'
                                     '        1.377         0.02          0.34          190.0         \n'
                                     '        1.377         0.02          0.23          170.0         \n'
                                     '        1.377         0.02          0.15          176.0         \n'
                                     '        1.377         0.02          0.07          164.0         \n'
                                     '        1.377         0.02          -0.01         156.0         \n'
                                     '        1.377         0.02          -0.11         158.0         \n'
                                     '        1.377         0.02          -0.18         150.0         \n'
                                     '        1.377         0.02          -0.28         144.0         \n'
                                     '        1.377         0.02          -0.35         143.0         \n'
                                     '        1.377         0.02          -0.44         140.0         \n'
                                     '        1.377         0.02          -0.54         145.0         \n'
                                     '        1.377         0.02          -0.63         157.0         \n'
                                     '        1.377         0.02          -0.71         155.0         \n'
                                     '        1.377         0.02          -0.79         158.0         \n'
                                     '        1.377         0.02          -0.88         145.0         \n'
                                     '        1.377         0.02          -0.98         100.0         \n'
                                     '        1.595         0.02          0.44          320.0         \n'
                                     '        1.595         0.02          0.35          303.0         \n'
                                     '        1.595         0.02          0.26          265.0         \n'
                                     '        1.595         0.02          0.16          225.0         \n'
                                     '        1.595         0.02          0.08          223.0         \n'
                                     '        1.595         0.02          -0.02         203.0         \n'
                                     '        1.595         0.02          -0.11         195.0         \n'
                                     '        1.595         0.02          -0.18         170.0         \n'
                                     '        1.595         0.02          -0.27         168.0         \n'
                                     '        1.595         0.02          -0.36         150.0         \n'
                                     '        1.595         0.02          -0.46         160.0         \n'
                                     '        1.595         0.02          -0.53         135.0         \n'
                                     '        1.595         0.02          -0.64         150.0         \n'
                                     '        1.595         0.02          -0.73         125.0         \n'
                                     '        1.595         0.02          -0.82         110.0         \n'
                                     '        1.595         0.02          -0.92         100.0         \n'
                                     '        1.682         0.02          0.5           170.0         \n'
                                     '        1.682         0.02          0.36          153.0         \n'
                                     '        1.682         0.02          0.26          160.0         \n'
                                     '        1.682         0.02          0.16          143.0         \n'
                                     '        1.682         0.02          0.07          150.0         \n'
                                     '        1.682         0.02          -0.05         130.0         \n'
                                     '        1.682         0.02          -0.14         143.0         \n'
                                     '        1.682         0.02          -0.25         140.0         \n'
                                     '        1.682         0.02          -0.34         138.0         \n'
                                     '        1.682         0.02          -0.45         140.0         \n'
                                     '        1.682         0.02          -0.54         140.0         \n'
                                     '        1.682         0.02          -0.66         150.0         \n'
                                     '        1.682         0.02          -0.76         140.0         \n'
                                     '        1.682         0.02          -0.87         125.0         \n'
                                     '        1.682         0.02          -0.97         80.0          \n'
                                     '        1.756         0.025         0.5           193.0         \n'
                                     '        1.756         0.025         0.4           163.0         \n'
                                     '        1.756         0.025         0.3           155.0         \n'
                                     '        1.756         0.025         0.21          137.0         \n'
                                     '        1.756         0.025         0.09          124.0         \n'
                                     '        1.756         0.025         0.0           123.0         \n'
                                     '        1.756         0.025         -0.09         127.0         \n'
                                     '        1.756         0.025         -0.19         122.0         \n'
                                     '        1.756         0.025         -0.28         128.0         \n'
                                     '        1.756         0.025         -0.38         145.0         \n'
                                     '        1.756         0.025         -0.47         144.0         \n'
                                     '        1.756         0.025         -0.59         178.0         \n'
                                     '        1.756         0.025         -0.69         210.0         \n'
                                     '        1.756         0.025         -0.79         221.0         \n'
                                     '        1.756         0.025         -0.88         245.0         \n'
                                     '        1.779         0.025         0.53          170.0         \n'
                                     '        1.779         0.025         0.42          148.0         \n'
                                     '        1.779         0.025         0.32          140.0         \n'
                                     '        1.779         0.025         0.23          130.0         \n'
                                     '        1.779         0.025         0.13          125.0         \n'
                                     '        1.779         0.025         0.03          130.0         \n'
                                     '        1.779         0.025         -0.06         120.0         \n'
                                     '        1.779         0.025         -0.15         120.0         \n'
                                     '        1.779         0.025         -0.25         125.0         \n'
                                     '        1.779         0.025         -0.34         130.0         \n'
                                     '        1.779         0.025         -0.44         140.0         \n'
                                     '        1.779         0.025         -0.54         180.0         \n'
                                     '        1.779         0.025         -0.64         198.0         \n'
                                     '        1.779         0.025         -0.73         230.0         \n'
                                     '        1.779         0.025         -0.83         260.0         \n'
                                     '        1.779         0.025         -0.92         240.0         \n'
                                     '        1.796         0.025         0.47          181.0         \n'
                                     '        1.796         0.025         0.4           146.0         \n'
                                     '        1.796         0.025         0.3           138.0         \n'
                                     '        1.796         0.025         0.2           125.0         \n'
                                     '        1.796         0.025         0.11          121.0         \n'
                                     '        1.796         0.025         0.01          125.0         \n'
                                     '        1.796         0.025         -0.1          118.0         \n'
                                     '        1.796         0.025         -0.18         106.0         \n'
                                     '        1.796         0.025         -0.27         135.0         \n'
                                     '        1.796         0.025         -0.36         133.0         \n'
                                     '        1.796         0.025         -0.46         141.0         \n'
                                     '        1.796         0.025         -0.56         142.0         \n'
                                     '        1.796         0.025         -0.67         158.0         \n'
                                     '        1.796         0.025         -0.75         178.0         \n'
                                     '        1.796         0.025         -0.86         208.0         \n'
                                     '        2.07          0.02          0.52          145.0         \n'
                                     '        2.07          0.02          0.42          135.0         \n'
                                     '        2.07          0.02          0.33          135.0         \n'
                                     '        2.07          0.02          0.24          126.0         \n'
                                     '        2.07          0.02          0.12          122.0         \n'
                                     '        2.07          0.02          0.03          120.0         \n'
                                     '        2.07          0.02          -0.06         114.0         \n'
                                     '        2.07          0.02          -0.16         127.0         \n'
                                     '        2.07          0.02          -0.26         110.0         \n'
                                     '        2.07          0.02          -0.36         108.0         \n'
                                     '        2.07          0.02          -0.44         117.0         \n'
                                     '        2.07          0.02          -0.54         115.0         \n'
                                     '        2.07          0.02          -0.64         115.0         \n'
                                     '        2.07          0.02          -0.73         110.0         \n'
                                     '        2.07          0.02          -0.82         110.0         \n'
                                     '        2.07          0.02          -0.92         95.0          \n'
                                     '        2.25          0.02          0.55          174.0         \n'
                                     '        2.25          0.02          0.46          155.0         \n'
                                     '        2.25          0.02          0.39          149.0         \n'
                                     '        2.25          0.02          0.3           137.0         \n'
                                     '        2.25          0.02          0.21          128.0         \n'
                                     '        2.25          0.02          0.12          116.0         \n'
                                     '        2.25          0.02          0.02          103.0         \n'
                                     '        2.25          0.02          -0.08         105.0         \n'
                                     '        2.25          0.02          -0.18         108.0         \n'
                                     '        2.25          0.02          -0.26         102.0         \n'
                                     '        2.25          0.02          -0.32         103.0         \n'
                                     '        2.25          0.02          -0.42         92.0          \n'
                                     '        2.25          0.02          -0.5          81.0          \n'
                                     '        2.25          0.02          -0.59         78.0          \n'
                                     '        2.25          0.02          -0.67         96.0          \n'
                                     '        2.25          0.02          -0.76         73.0          \n'
                                     '        2.25          0.02          -0.85         77.0          \n'
                                     '        2.36          0.02          0.49          145.0         \n'
                                     '        2.36          0.02          0.41          140.0         \n'
                                     '        2.36          0.02          0.33          125.0         \n'
                                     '        2.36          0.02          0.25          106.0         \n'
                                     '        2.36          0.02          0.17          106.0         \n'
                                     '        2.36          0.02          0.07          105.0         \n'
                                     '        2.36          0.02          0.0           121.0         \n'
                                     '        2.36          0.02          -0.07         102.0         \n'
                                     '        2.36          0.02          -0.16         111.0         \n'
                                     '        2.36          0.02          -0.23         110.0         \n'
                                     '        2.36          0.02          -0.33         115.0         \n'
                                     '        2.36          0.02          -0.41         115.0         \n'
                                     '        2.36          0.02          -0.5          107.0         \n'
                                     '        2.36          0.02          -0.57         106.0         \n'
                                     '        2.36          0.02          -0.66         115.0         \n'
                                     '        2.36          0.02          -0.75         105.0         \n'
                                     '        2.36          0.02          -0.84         103.0         \n        ')
        simple = ds[('11314', '11314002', ' ')].getSimplified()
        # open( 'd', mode = 'w' ).writelines( str( simple ) )
        self.assertTablesAlmostEqual(str(simple),
                                     '#  Authors:   J.L.Fowler, C.H.Johnson\n'
                                     '#  Title:     Differential Elastic Scattering Cross Sections For Neutrons On Nitrogen.\n'
                                     '#  Year:      1955\n'
                                     '#  Institute: Oak Ridge National Laboratory, Oak Ridge, TN\n'
                                     '#  Reference: Physical Review 98, 728 (1955)\n'
                                     '#  Subent:    11314002\n'
                                     '#  Reaction:  Differential c/s with respect to angle for 14N(n,Elastic)14N \n'
                                     '#  Frame:     Center of mass\n'
                                     '#        Energy        Angle         Data          d(Energy)     \n'
                                     '#        MeV           degrees       barns/ster    MeV           \n'
                                     '        0.8           31.7883306171 0.164         0.025         \n'
                                     '        0.8           49.4583981265 0.17          0.025         \n'
                                     '        0.8           62.6128924973 0.157         0.025         \n'
                                     '        0.8           74.3357331486 0.167         0.025         \n'
                                     '        0.8           85.9860127819 0.151         0.025         \n'
                                     '        0.8           96.3153155694 0.156         0.025         \n'
                                     '        0.8           108.059230491 0.165         0.025         \n'
                                     '        0.8           120.663829742 0.143         0.025         \n'
                                     '        0.8           134.427004001 0.128         0.025         \n'
                                     '        0.97          60.659418425  0.09          0.01          \n'
                                     '        0.97          63.2563160496 0.088         0.01          \n'
                                     '        0.97          65.1654125103 0.083         0.01          \n'
                                     '        0.97          67.0455005986 0.076         0.01          \n'
                                     '        0.97          68.8998039759 0.076         0.01          \n'
                                     '        0.97          71.9407695092 0.076         0.01          \n'
                                     '        0.97          73.7397952917 0.08          0.01          \n'
                                     '        0.97          76.1134596374 0.083         0.01          \n'
                                     '        0.97          78.4630409672 0.082         0.01          \n'
                                     '        0.97          80.2121809433 0.078         0.01          \n'
                                     '        0.97          81.9521537527 0.078         0.01          \n'
                                     '        0.97          84.2608295227 0.075         0.01          \n'
                                     '        0.97          86.5601872325 0.076         0.01          \n'
                                     '        0.97          88.8540080016 0.078         0.01          \n'
                                     '        0.97          90.5729673449 0.08          0.01          \n'
                                     '        0.97          92.292442776  0.08          0.01          \n'
                                     '        0.97          94.5885657358 0.073         0.01          \n'
                                     '        0.97          96.8921025793 0.078         0.01          \n'
                                     '        0.97          99.2068962213 0.08          0.01          \n'
                                     '        0.97          100.952784199 0.07          0.01          \n'
                                     '        0.97          102.709032994 0.076         0.01          \n'
                                     '        0.97          105.070062145 0.076         0.01          \n'
                                     '        0.97          107.457603124 0.074         0.01          \n'
                                     '        0.97          109.87687407  0.073         0.01          \n'
                                     '        0.97          112.333682658 0.073         0.01          \n'
                                     '        0.97          114.204834801 0.07          0.01          \n'
                                     '        0.97          117.387107503 0.07          0.01          \n'
                                     '        0.97          119.340581575 0.066         0.01          \n'
                                     '        0.97          121.332251498 0.07          0.01          \n'
                                     '        0.97          122.683638846 0.065         0.01          \n'
                                     '        0.97          126.157008201 0.065         0.01          \n'
                                     '        0.97          128.316134474 0.07          0.01          \n'
                                     '        0.97          130.541601874 0.06          0.01          \n'
                                     '        0.97          132.843643044 0.07          0.01          \n'
                                     '        0.97          137.73141557  0.065         0.01          \n'
                                     '        0.97          139.464197889 0.065         0.01          \n'
                                     '        0.97          143.130102354 0.06          0.01          \n'
                                     '        0.97          147.140119621 0.063         0.01          \n'
                                     '        0.97          151.642363424 0.06          0.01          \n'
                                     '        0.97          155.505351529 0.055         0.01          \n'
                                     '        0.97          160.051556411 0.045         0.01          \n'
                                     '        0.97          168.521659045 0.04          0.01          \n'
                                     '        1.082         61.9657034651 0.148         0.005         \n'
                                     '        1.082         65.7951651985 0.135         0.005         \n'
                                     '        1.082         70.1231259299 0.145         0.005         \n'
                                     '        1.082         73.7397952917 0.133         0.005         \n'
                                     '        1.082         77.8776477552 0.126         0.005         \n'
                                     '        1.082         81.3730734413 0.125         0.005         \n'
                                     '        1.082         84.2608295227 0.135         0.005         \n'
                                     '        1.082         88.8540080016 0.145         0.005         \n'
                                     '        1.082         92.292442776  0.14          0.005         \n'
                                     '        1.082         96.3153155694 0.13          0.005         \n'
                                     '        1.082         100.369759805 0.13          0.005         \n'
                                     '        1.082         103.297071747 0.147         0.005         \n'
                                     '        1.082         107.457603124 0.139         0.005         \n'
                                     '        1.082         111.100196024 0.138         0.005         \n'
                                     '        1.082         115.467560142 0.143         0.005         \n'
                                     '        1.082         120.0         0.142         0.005         \n'
                                     '        1.082         123.367012969 0.14          0.005         \n'
                                     '        1.082         128.316134474 0.143         0.005         \n'
                                     '        1.082         132.843643044 0.14          0.005         \n'
                                     '        1.082         139.464197889 0.145         0.005         \n'
                                     '        1.082         144.095931417 0.13          0.005         \n'
                                     '        1.082         151.642363424 0.117         0.005         \n'
                                     '        1.082         160.051556411 0.11          0.005         \n'
                                     '        1.11          61.9657034651 0.214         0.005         \n'
                                     '        1.11          65.1654125103 0.204         0.005         \n'
                                     '        1.11          68.8998039759 0.194         0.005         \n'
                                     '        1.11          72.5423968763 0.186         0.005         \n'
                                     '        1.11          76.7029282528 0.182         0.005         \n'
                                     '        1.11          80.2121809433 0.18          0.005         \n'
                                     '        1.11          83.1078974207 0.178         0.005         \n'
                                     '        1.11          87.1340160174 0.172         0.005         \n'
                                     '        1.11          91.1459919984 0.169         0.005         \n'
                                     '        1.11          94.0139872181 0.174         0.005         \n'
                                     '        1.11          98.0478462473 0.168         0.005         \n'
                                     '        1.11          101.536959033 0.17          0.005         \n'
                                     '        1.11          105.070062145 0.178         0.005         \n'
                                     '        1.11          108.662924885 0.178         0.005         \n'
                                     '        1.11          112.954499401 0.187         0.005         \n'
                                     '        1.11          116.103881137 0.195         0.005         \n'
                                     '        1.11          120.0         0.19          0.005         \n'
                                     '        1.11          124.055797743 0.195         0.005         \n'
                                     '        1.11          129.050122536 0.202         0.005         \n'
                                     '        1.11          133.630108868 0.185         0.005         \n'
                                     '        1.11          139.464197889 0.207         0.005         \n'
                                     '        1.11          144.095931417 0.185         0.005         \n'
                                     '        1.12          61.9657034651 0.315         0.005         \n'
                                     '        1.12          64.5324398575 0.27          0.005         \n'
                                     '        1.12          68.2843827167 0.22          0.005         \n'
                                     '        1.12          72.5423968763 0.23          0.005         \n'
                                     '        1.12          76.7029282528 0.22          0.005         \n'
                                     '        1.12          79.6302401945 0.205         0.005         \n'
                                     '        1.12          83.1078974207 0.19          0.005         \n'
                                     '        1.12          86.5601872325 0.215         0.005         \n'
                                     '        1.12          90.0          0.185         0.005         \n'
                                     '        1.12          93.4398127675 0.195         0.005         \n'
                                     '        1.12          96.8921025793 0.185         0.005         \n'
                                     '        1.12          100.369759805 0.175         0.005         \n'
                                     '        1.12          103.297071747 0.175         0.005         \n'
                                     '        1.12          107.457603124 0.175         0.005         \n'
                                     '        1.12          111.715617283 0.18          0.005         \n'
                                     '        1.12          115.467560142 0.175         0.005         \n'
                                     '        1.12          118.034296535 0.18          0.005         \n'
                                     '        1.12          122.683638846 0.17          0.005         \n'
                                     '        1.12          126.869897646 0.19          0.005         \n'
                                     '        1.12          131.299872792 0.175         0.005         \n'
                                     '        1.12          136.886394054 0.185         0.005         \n'
                                     '        1.12          143.130102354 0.18          0.005         \n'
                                     '        1.12          149.316582891 0.17          0.005         \n'
                                     '        1.12          154.158067237 0.145         0.005         \n'
                                     '        1.12          168.521659045 0.13          0.005         \n'
                                     '        1.13          61.3145979859 0.26          0.005         \n'
                                     '        1.13          65.1654125103 0.24          0.005         \n'
                                     '        1.13          68.8998039759 0.207         0.005         \n'
                                     '        1.13          72.5423968763 0.198         0.005         \n'
                                     '        1.13          75.5224878141 0.202         0.005         \n'
                                     '        1.13          79.6302401945 0.182         0.005         \n'
                                     '        1.13          83.1078974207 0.171         0.005         \n'
                                     '        1.13          87.1340160174 0.172         0.005         \n'
                                     '        1.13          90.0          0.155         0.005         \n'
                                     '        1.13          93.4398127675 0.165         0.005         \n'
                                     '        1.13          96.8921025793 0.156         0.005         \n'
                                     '        1.13          101.536959033 0.142         0.005         \n'
                                     '        1.13          104.477512186 0.134         0.005         \n'
                                     '        1.13          108.662924885 0.14          0.005         \n'
                                     '        1.13          111.715617283 0.13          0.005         \n'
                                     '        1.13          116.103881137 0.124         0.005         \n'
                                     '        1.13          120.663829742 0.133         0.005         \n'
                                     '        1.13          124.055797743 0.133         0.005         \n'
                                     '        1.13          128.316134474 0.129         0.005         \n'
                                     '        1.13          132.843643044 0.119         0.005         \n'
                                     '        1.13          137.73141557  0.14          0.005         \n'
                                     '        1.13          143.130102354 0.121         0.005         \n'
                                     '        1.13          149.316582891 0.128         0.005         \n'
                                     '        1.13          156.926081934 0.114         0.005         \n'
                                     '        1.16          63.2563160496 0.132         0.005         \n'
                                     '        1.16          67.3562597371 0.135         0.005         \n'
                                     '        1.16          70.7312245085 0.127         0.005         \n'
                                     '        1.16          74.3357331486 0.117         0.005         \n'
                                     '        1.16          78.4630409672 0.116         0.005         \n'
                                     '        1.16          81.3730734413 0.12          0.005         \n'
                                     '        1.16          85.4114342642 0.125         0.005         \n'
                                     '        1.16          87.707557224  0.11          0.005         \n'
                                     '        1.16          91.7191313209 0.1           0.005         \n'
                                     '        1.16          94.0139872181 0.105         0.005         \n'
                                     '        1.16          98.0478462473 0.095         0.005         \n'
                                     '        1.16          101.536959033 0.105         0.005         \n'
                                     '        1.16          105.070062145 0.099         0.005         \n'
                                     '        1.16          108.662924885 0.11          0.005         \n'
                                     '        1.16          112.333682658 0.1           0.005         \n'
                                     '        1.16          115.467560142 0.11          0.005         \n'
                                     '        1.16          120.0         0.099         0.005         \n'
                                     '        1.16          123.367012969 0.105         0.005         \n'
                                     '        1.16          128.316134474 0.105         0.005         \n'
                                     '        1.16          132.067064802 0.099         0.005         \n'
                                     '        1.16          136.886394054 0.102         0.005         \n'
                                     '        1.16          141.260575402 0.105         0.005         \n'
                                     '        1.16          147.140119621 0.098         0.005         \n'
                                     '        1.16          154.158067237 0.09          0.005         \n'
                                     '        1.16          163.739795292 0.067         0.005         \n'
                                     '        1.35          58.6677485024 0.215         0.01          \n'
                                     '        1.35          65.7951651985 0.224         0.01          \n'
                                     '        1.35          70.7312245085 0.185         0.01          \n'
                                     '        1.35          76.7029282528 0.18          0.01          \n'
                                     '        1.35          81.9521537527 0.18          0.01          \n'
                                     '        1.35          87.1340160174 0.17          0.01          \n'
                                     '        1.35          92.292442776  0.163         0.01          \n'
                                     '        1.35          97.4695923164 0.18          0.01          \n'
                                     '        1.35          102.709032994 0.168         0.01          \n'
                                     '        1.35          109.268775491 0.179         0.01          \n'
                                     '        1.35          112.954499401 0.193         0.01          \n'
                                     '        1.35          118.034296535 0.187         0.01          \n'
                                     '        1.35          124.750225754 0.203         0.01          \n'
                                     '        1.35          130.541601874 0.21          0.01          \n'
                                     '        1.35          136.886394054 0.218         0.01          \n'
                                     '        1.35          144.095931417 0.227         0.01          \n'
                                     '        1.35          156.926081934 0.233         0.01          \n'
                                     '        1.377         57.9945451722 0.21          0.01          \n'
                                     '        1.377         64.5324398575 0.192         0.01          \n'
                                     '        1.377         70.1231259299 0.19          0.01          \n'
                                     '        1.377         76.7029282528 0.17          0.01          \n'
                                     '        1.377         81.3730734413 0.176         0.01          \n'
                                     '        1.377         85.9860127819 0.164         0.01          \n'
                                     '        1.377         90.5729673449 0.156         0.01          \n'
                                     '        1.377         96.3153155694 0.158         0.01          \n'
                                     '        1.377         100.369759805 0.15          0.01          \n'
                                     '        1.377         106.260204708 0.144         0.01          \n'
                                     '        1.377         110.487315115 0.143         0.01          \n'
                                     '        1.377         116.103881137 0.14          0.01          \n'
                                     '        1.377         122.683638846 0.145         0.01          \n'
                                     '        1.377         129.050122536 0.157         0.01          \n'
                                     '        1.377         135.234915329 0.155         0.01          \n'
                                     '        1.377         142.185511494 0.158         0.01          \n'
                                     '        1.377         151.642363424 0.145         0.01          \n'
                                     '        1.377         168.521659045 0.1           0.01          \n'
                                     '        1.595         63.8961188627 0.32          0.01          \n'
                                     '        1.595         69.5126848853 0.303         0.01          \n'
                                     '        1.595         74.9299378551 0.265         0.01          \n'
                                     '        1.595         80.7931037787 0.225         0.01          \n'
                                     '        1.595         85.4114342642 0.223         0.01          \n'
                                     '        1.595         91.1459919984 0.203         0.01          \n'
                                     '        1.595         96.3153155694 0.195         0.01          \n'
                                     '        1.595         100.369759805 0.17          0.01          \n'
                                     '        1.595         105.664266851 0.168         0.01          \n'
                                     '        1.595         111.100196024 0.15          0.01          \n'
                                     '        1.595         117.387107503 0.16          0.01          \n'
                                     '        1.595         122.005454828 0.135         0.01          \n'
                                     '        1.595         129.7918195   0.15          0.01          \n'
                                     '        1.595         136.886394054 0.125         0.01          \n'
                                     '        1.595         145.084793753 0.11          0.01          \n'
                                     '        1.595         156.926081934 0.1           0.01          \n'
                                     '        1.682         60.0          0.17          0.01          \n'
                                     '        1.682         68.8998039759 0.153         0.01          \n'
                                     '        1.682         74.9299378551 0.16          0.01          \n'
                                     '        1.682         80.7931037787 0.143         0.01          \n'
                                     '        1.682         85.9860127819 0.15          0.01          \n'
                                     '        1.682         92.8659839826 0.13          0.01          \n'
                                     '        1.682         98.0478462473 0.143         0.01          \n'
                                     '        1.682         104.477512186 0.14          0.01          \n'
                                     '        1.682         109.87687407  0.138         0.01          \n'
                                     '        1.682         116.74368395  0.14          0.01          \n'
                                     '        1.682         122.683638846 0.14          0.01          \n'
                                     '        1.682         131.299872792 0.15          0.01          \n'
                                     '        1.682         139.464197889 0.14          0.01          \n'
                                     '        1.682         150.4586395   0.125         0.01          \n'
                                     '        1.682         165.930132252 0.08          0.01          \n'
                                     '        1.756         60.0          0.193         0.0125        \n'
                                     '        1.756         66.4218215218 0.163         0.0125        \n'
                                     '        1.756         72.5423968763 0.155         0.0125        \n'
                                     '        1.756         77.8776477552 0.137         0.0125        \n'
                                     '        1.756         84.8363929092 0.124         0.0125        \n'
                                     '        1.756         90.0          0.123         0.0125        \n'
                                     '        1.756         95.1636070908 0.127         0.0125        \n'
                                     '        1.756         100.952784199 0.122         0.0125        \n'
                                     '        1.756         106.260204708 0.128         0.0125        \n'
                                     '        1.756         112.333682658 0.145         0.0125        \n'
                                     '        1.756         118.034296535 0.144         0.0125        \n'
                                     '        1.756         126.157008201 0.178         0.0125        \n'
                                     '        1.756         133.630108868 0.21          0.0125        \n'
                                     '        1.756         142.185511494 0.221         0.0125        \n'
                                     '        1.756         151.642363424 0.245         0.0125        \n'
                                     '        1.779         57.9945451722 0.17          0.0125        \n'
                                     '        1.779         65.1654125103 0.148         0.0125        \n'
                                     '        1.779         71.3370751151 0.14          0.0125        \n'
                                     '        1.779         76.7029282528 0.13          0.0125        \n'
                                     '        1.779         82.5304076836 0.125         0.0125        \n'
                                     '        1.779         88.2808686791 0.13          0.0125        \n'
                                     '        1.779         93.4398127675 0.12          0.0125        \n'
                                     '        1.779         98.6269265587 0.12          0.0125        \n'
                                     '        1.779         104.477512186 0.125         0.0125        \n'
                                     '        1.779         109.87687407  0.13          0.0125        \n'
                                     '        1.779         116.103881137 0.14          0.0125        \n'
                                     '        1.779         122.683638846 0.18          0.0125        \n'
                                     '        1.779         129.7918195   0.198         0.0125        \n'
                                     '        1.779         136.886394054 0.23          0.0125        \n'
                                     '        1.779         146.098738003 0.26          0.0125        \n'
                                     '        1.779         156.926081934 0.24          0.0125        \n'
                                     '        1.796         61.9657034651 0.181         0.0125        \n'
                                     '        1.796         66.4218215218 0.146         0.0125        \n'
                                     '        1.796         72.5423968763 0.138         0.0125        \n'
                                     '        1.796         78.4630409672 0.125         0.0125        \n'
                                     '        1.796         83.6846844306 0.121         0.0125        \n'
                                     '        1.796         89.4270326551 0.125         0.0125        \n'
                                     '        1.796         95.7391704773 0.118         0.0125        \n'
                                     '        1.796         100.369759805 0.106         0.0125        \n'
                                     '        1.796         105.664266851 0.135         0.0125        \n'
                                     '        1.796         111.100196024 0.133         0.0125        \n'
                                     '        1.796         117.387107503 0.141         0.0125        \n'
                                     '        1.796         124.055797743 0.142         0.0125        \n'
                                     '        1.796         132.067064802 0.158         0.0125        \n'
                                     '        1.796         138.590377891 0.178         0.0125        \n'
                                     '        1.796         149.316582891 0.208         0.0125        \n'
                                     '        2.07          58.6677485024 0.145         0.01          \n'
                                     '        2.07          65.1654125103 0.135         0.01          \n'
                                     '        2.07          70.7312245085 0.135         0.01          \n'
                                     '        2.07          76.1134596374 0.126         0.01          \n'
                                     '        2.07          83.1078974207 0.122         0.01          \n'
                                     '        2.07          88.2808686791 0.12          0.01          \n'
                                     '        2.07          93.4398127675 0.114         0.01          \n'
                                     '        2.07          99.2068962213 0.127         0.01          \n'
                                     '        2.07          105.070062145 0.11          0.01          \n'
                                     '        2.07          111.100196024 0.108         0.01          \n'
                                     '        2.07          116.103881137 0.117         0.01          \n'
                                     '        2.07          122.683638846 0.115         0.01          \n'
                                     '        2.07          129.7918195   0.115         0.01          \n'
                                     '        2.07          136.886394054 0.11          0.01          \n'
                                     '        2.07          145.084793753 0.11          0.01          \n'
                                     '        2.07          156.926081934 0.095         0.01          \n'
                                     '        2.25          56.6329870308 0.174         0.01          \n'
                                     '        2.25          62.6128924973 0.155         0.01          \n'
                                     '        2.25          67.0455005986 0.149         0.01          \n'
                                     '        2.25          72.5423968763 0.137         0.01          \n'
                                     '        2.25          77.8776477552 0.128         0.01          \n'
                                     '        2.25          83.1078974207 0.116         0.01          \n'
                                     '        2.25          88.8540080016 0.103         0.01          \n'
                                     '        2.25          94.5885657358 0.105         0.01          \n'
                                     '        2.25          100.369759805 0.108         0.01          \n'
                                     '        2.25          105.070062145 0.102         0.01          \n'
                                     '        2.25          108.662924885 0.103         0.01          \n'
                                     '        2.25          114.83458749  0.092         0.01          \n'
                                     '        2.25          120.0         0.081         0.01          \n'
                                     '        2.25          126.157008201 0.078         0.01          \n'
                                     '        2.25          132.067064802 0.096         0.01          \n'
                                     '        2.25          139.464197889 0.073         0.01          \n'
                                     '        2.25          148.211669383 0.077         0.01          \n'
                                     '        2.36          60.659418425  0.145         0.01          \n'
                                     '        2.36          65.7951651985 0.14          0.01          \n'
                                     '        2.36          70.7312245085 0.125         0.01          \n'
                                     '        2.36          75.5224878141 0.106         0.01          \n'
                                     '        2.36          80.2121809433 0.106         0.01          \n'
                                     '        2.36          85.9860127819 0.105         0.01          \n'
                                     '        2.36          90.0          0.121         0.01          \n'
                                     '        2.36          94.0139872181 0.102         0.01          \n'
                                     '        2.36          99.2068962213 0.111         0.01          \n'
                                     '        2.36          103.297071747 0.11          0.01          \n'
                                     '        2.36          109.268775491 0.115         0.01          \n'
                                     '        2.36          114.204834801 0.115         0.01          \n'
                                     '        2.36          120.0         0.107         0.01          \n'
                                     '        2.36          124.750225754 0.106         0.01          \n'
                                     '        2.36          131.299872792 0.115         0.01          \n'
                                     '        2.36          138.590377891 0.105         0.01          \n'
                                     '        2.36          147.140119621 0.103         0.01          \n        ')

    def test_nubar(self):
        subent = self.dbMgr.retrieve(SUBENT='12326006', rawEntry=True)
        ds = exfor_entry.X4Entry(subent['12326']).getDataSets()
        fullanswer = '#  Authors:   J.C.Hopkins, B.C.Diven\n' \
                     '#  Title:     Prompt Neutrons From Fission.\n' \
                     '#  Year:      1963\n' \
                     '#  Institute: Los Alamos National Laboratory, NM\n' \
                     '#  Reference: Nuclear Physics 48, 433 (1963)\n' \
                     '#  Subent:    12326006\n' \
                     '#  Reaction:  Prompt neutron yield (nu-bar) for 239Pu(n,Fission) \n' \
                     '#        MONIT         EN            EN-RSL        DATA          ERR-SYS       ERR-T         \n' \
                     '#        PRT/FIS       MEV           MEV           PRT/FIS       PRT/FIS       PRT/FIS       \n' \
                     '        3.771         0.25          0.05          2.931         0.029         0.039         \n' \
                     '        3.771         0.42          0.11          2.957         0.03          0.046         \n' \
                     '        3.771         0.61          0.07          2.904         0.029         0.041         \n' \
                     '        3.771         0.9           0.08          3.004         0.03          0.041         \n' \
                     '        3.771         3.9           0.29          3.422         0.038         0.039         \n' \
                     '        3.771         14.5          1.0           4.942         0.076         0.119         \n' \
                     '        '
        #open( 'a', mode = 'w' ).writelines(fullanswer)
        #open( 'b', mode = 'w' ).writelines( str( ds[ ('12326', '12326006', ' ') ] ) )
        self.assertTablesAlmostEqual(str(ds[('12326', '12326006', ' ')]), fullanswer)
        simple = ds[('12326', '12326006', ' ')].getSimplified()
        simpleanswer = '#  Authors:   J.C.Hopkins, B.C.Diven\n' \
                       '#  Title:     Prompt Neutrons From Fission.\n' \
                       '#  Year:      1963\n' \
                       '#  Institute: Los Alamos National Laboratory, NM\n' \
                       '#  Reference: Nuclear Physics 48, 433 (1963)\n' \
                       '#  Subent:    12326006\n' \
                       '#  Reaction:  Prompt neutron yield (nu-bar) for 239Pu(n,Fission) \n' \
                       '#        Energy        Data          d(Energy)     d(Data)       \n' \
                       '#        MeV           ptcls/fis     MeV           ptcls/fis     \n' \
                       '        0.25          2.931         0.025         0.039         \n' \
                       '        0.42          2.957         0.055         0.046         \n' \
                       '        0.61          2.904         0.035         0.041         \n' \
                       '        0.9           3.004         0.04          0.041         \n' \
                       '        3.9           3.422         0.145         0.039         \n' \
                       '        14.5          4.942         0.5           0.119         \n' \
                       '        '
        #open( 'c', mode = 'w' ).writelines( str( simpleanswer ) )
        #open( 'd', mode = 'w' ).writelines( str( simple ) )
        self.assertTablesAlmostEqual(str(simple), simpleanswer)

    def test_energy_spectrum(self):
        subent = self.dbMgr.retrieve(SUBENT='20576003', rawEntry=True)
        ds = exfor_entry.X4Entry(subent['20576']).getDataSets()
        # open( 'c', mode = 'w' ).writelines( str( ds[ ('20576', '20576003', ' ') ] ) )
        answer = """
#  Authors:   H.Knitter
#  Title:     -Measurement Of The Energy Spectrum Of Prompt Neutrons From The Fission Of Pu239 By 0.215 Mev Neutrons-
#  Year:      1975
#  Institute: Inst. for Ref. Mat. and Meas. (IRNM), Geel
#  Reference: Atomkernenergie 26, 76 (1975)
#  Subent:    20576003
#  Reaction:  Relative data  for 239Pu(n,Fission) Reference quantity not given
#        EN            EN-RSL        E             E-RSL         DATA          DATA-ERR      ERR-1
#        KEV           KEV           MEV           MEV           ARB-UNITS     ARB-UNITS     PER-CENT
        215.0         32.0          0.28          0.01          66.8          2.5           2.0
        215.0         32.0          0.31          0.01          70.2          2.4           2.0
        215.0         32.0          0.34          0.01          65.1          2.2           2.0
        215.0         32.0          0.36          0.01          70.5          2.2           2.0
        215.0         32.0          0.39          0.01          68.8          2.1           2.0
        215.0         32.0          0.41          0.01          74.2          2.1           2.0
        215.0         32.0          0.44          0.01          75.6          2.2           2.0
        215.0         32.0          0.46          0.01          74.8          2.1           2.0
        215.0         32.0          0.49          0.01          74.8          2.1           2.0
        215.0         32.0          0.51          0.01          73.6          2.0           2.0
        215.0         32.0          0.54          0.01          74.2          2.0           2.0
        215.0         32.0          0.56          0.01          75.7          2.0           2.0
        215.0         32.0          0.59          0.01          75.8          2.0           2.0
        215.0         32.0          0.61          0.01          76.6          2.1           2.0
        215.0         32.0          0.63          0.01          75.4          2.0           2.0
        215.0         32.0          0.66          0.01          78.7          2.1           2.0
        215.0         32.0          0.69          0.01          76.3          2.0           2.0
        215.0         32.0          0.71          0.01          78.6          2.1           2.0
        215.0         32.0          0.73          0.01          74.6          2.1           2.0
        215.0         32.0          0.76          0.01          78.7          2.0           2.0
        215.0         32.0          0.79          0.02          79.4          2.1           2.0
        215.0         32.0          0.81          0.02          78.3          2.1           2.0
        215.0         32.0          0.84          0.02          76.6          2.0           2.0
        215.0         32.0          0.86          0.02          80.0          2.2           2.0
        215.0         32.0          0.89          0.02          81.0          2.1           2.0
        215.0         32.0          0.91          0.02          80.2          2.1           2.0
        215.0         32.0          0.94          0.02          79.5          2.1           2.0
        215.0         32.0          0.96          0.02          78.4          2.1           2.0
        215.0         32.0          0.98          0.02          77.8          2.1           2.0
        215.0         32.0          1.01          0.02          76.8          2.2           2.0
        215.0         32.0          1.04          0.02          78.4          2.0           2.0
        215.0         32.0          1.06          0.02          78.3          2.2           2.0
        215.0         32.0          1.09          0.02          77.8          2.1           2.0
        215.0         32.0          1.11          0.02          74.9          2.1           2.0
        215.0         32.0          1.13          0.03          75.1          2.1           2.0
        215.0         32.0          1.16          0.03          76.0          2.1           2.0
        215.0         32.0          1.19          0.03          76.1          2.1           2.0
        215.0         32.0          1.21          0.03          74.0          2.0           2.0
        215.0         32.0          1.24          0.03          73.5          2.2           2.0
        215.0         32.0          1.26          0.03          76.7          1.6           2.0
        215.0         32.0          1.29          0.03          74.5          1.6           2.0
        215.0         32.0          1.32          0.03          72.3          1.5           2.0
        215.0         32.0          1.35          0.03          72.8          1.5           2.0
        215.0         32.0          1.39          0.04          72.2          1.5           2.0
        215.0         32.0          1.42          0.04          72.1          1.5           2.0
        215.0         32.0          1.45          0.04          69.1          1.7           2.0
        215.0         32.0          1.47          0.04          70.7          1.8           2.0
        215.0         32.0          1.5           0.04          71.3          1.8           2.0
        215.0         32.0          1.52          0.04          67.3          1.7           2.0
        215.0         32.0          1.55          0.04          68.4          1.7           2.0
        215.0         32.0          1.58          0.04          65.1          1.6           2.0
        215.0         32.0          1.6           0.04          65.7          1.6           2.0
        215.0         32.0          1.63          0.04          64.3          1.6           2.0
        215.0         32.0          1.66          0.05          64.1          1.6           2.0
        215.0         32.0          1.69          0.05          64.7          1.6           2.0
        215.0         32.0          1.72          0.05          61.9          1.5           2.0
        215.0         32.0          1.75          0.05          63.1          1.5           2.0
        215.0         32.0          1.79          0.05          63.0          1.5           2.0
        215.0         32.0          1.82          0.05          60.9          1.5           2.0
        215.0         32.0          1.85          0.05          59.9          1.5           2.0
        215.0         32.0          1.89          0.06          58.7          1.4           2.0
        215.0         32.0          1.93          0.06          58.0          1.4           2.0
        215.0         32.0          1.96          0.06          57.0          1.4           2.0
        215.0         32.0          2.0           0.06          56.1          1.4           2.0
        215.0         32.0          2.04          0.06          54.6          1.3           2.0
        215.0         32.0          2.07          0.06          54.1          1.8           2.0
        215.0         32.0          2.09          0.06          52.7          1.8           2.0
        215.0         32.0          2.11          0.07          52.0          1.8           2.0
        215.0         32.0          2.14          0.07          51.6          1.8           2.0
        215.0         32.0          2.16          0.07          52.9          1.8           2.0
        215.0         32.0          2.18          0.07          51.0          1.7           2.0
        215.0         32.0          2.2           0.07          51.0          1.7           2.0
        215.0         32.0          2.22          0.07          49.6          1.7           2.0
        215.0         32.0          2.25          0.07          48.9          1.7           2.0
        215.0         32.0          2.27          0.07          47.3          1.6           2.0
        215.0         32.0          2.29          0.07          49.5          1.7           2.0
        215.0         32.0          2.32          0.07          46.6          1.6           None
        215.0         32.0          2.34          0.07          45.4          1.6           None
        215.0         32.0          2.37          0.08          46.2          1.6           None
        215.0         32.0          2.39          0.08          46.6          1.6           None
        215.0         32.0          2.42          0.08          45.3          1.5           None
        215.0         32.0          2.44          0.08          44.0          1.5           None
        215.0         32.0          2.47          0.08          44.6          1.5           None
        215.0         32.0          2.5           0.08          41.6          1.4           None
        215.0         32.0          2.53          0.09          43.4          1.5           None
        215.0         32.0          2.56          0.09          41.3          1.4           None
        215.0         32.0          2.58          0.09          43.2          1.5           None
        215.0         32.0          2.61          0.09          41.4          1.4           None
        215.0         32.0          2.64          0.09          39.5          1.4           None
        215.0         32.0          2.67          0.09          38.9          1.3           None
        215.0         32.0          2.7           0.09          39.7          1.4           None
        215.0         32.0          2.73          0.1           37.5          1.3           None
        215.0         32.0          2.76          0.1           36.4          1.2           None
        215.0         32.0          2.79          0.1           36.1          1.2           None
        215.0         32.0          2.82          0.1           36.6          1.2           None
        215.0         32.0          2.86          0.1           36.2          1.2           None
        215.0         32.0          2.89          0.1           34.8          1.2           None
        215.0         32.0          2.93          0.1           34.0          1.2           None
        215.0         32.0          2.96          0.1           34.1          1.2           None
        215.0         32.0          3.0           0.11          33.4          1.2           None
        215.0         32.0          3.03          0.11          31.2          1.1           None
        215.0         32.0          3.07          0.11          32.4          1.1           None
        215.0         32.0          3.11          0.11          31.5          1.1           None
        215.0         32.0          3.15          0.12          30.7          1.1           None
        215.0         32.0          3.18          0.12          29.3          1.0           None
        215.0         32.0          3.22          0.12          28.6          1.0           None
        215.0         32.0          3.26          0.12          28.3          1.0           None
        215.0         32.0          3.3           0.12          27.1          1.0           None
        215.0         32.0          3.34          0.13          27.6          1.0           None
        215.0         32.0          3.39          0.13          26.3          0.9           None
        215.0         32.0          3.43          0.13          25.4          0.9           None
        215.0         32.0          3.48          0.14          24.6          0.9           None
        215.0         32.0          3.52          0.14          24.4          0.9           None
        215.0         32.0          3.57          0.14          23.7          0.8           None
        215.0         32.0          3.61          0.14          22.4          0.8           None
        215.0         32.0          3.66          0.15          21.7          0.8           None
        215.0         32.0          3.71          0.15          22.5          0.8           None
        215.0         32.0          3.76          0.15          21.1          0.8           None
        215.0         32.0          3.81          0.155         20.0          0.7           None
        215.0         32.0          3.86          0.155         19.0          0.7           None
        215.0         32.0          3.92          0.165         19.4          0.7           None
        215.0         32.0          3.97          0.165         17.7          0.7           None
        215.0         32.0          4.03          0.165         18.0          0.7           None
        215.0         32.0          4.08          0.175         16.6          0.6           None
        215.0         32.0          4.14          0.175         16.7          0.6           None
        215.0         32.0          4.2           0.18          16.0          0.6           None
        215.0         32.0          4.26          0.185         15.3          0.6           None
        215.0         32.0          4.32          0.185         15.2          0.6           None
        215.0         32.0          4.38          0.195         14.5          0.6           None
        215.0         32.0          4.45          0.195         13.2          0.5           None
        215.0         32.0          4.51          0.2           13.2          0.5           None
        215.0         32.0          4.57          0.205         13.1          0.5           None
        215.0         32.0          4.64          0.21          12.4          0.5           None
        215.0         32.0          4.72          0.215         12.3          0.5           None
        215.0         32.0          4.79          0.22          11.3          0.5           None
        215.0         32.0          4.86          0.225         10.8          0.4           None
        215.0         32.0          4.94          0.23          9.73          0.42          None
        215.0         32.0          5.01          0.235         10.0          0.4           None
        215.0         32.0          5.09          0.24          9.56          0.41          None
        215.0         32.0          5.17          0.245         8.77          0.39          None
        215.0         32.0          5.25          0.25          8.61          0.38          None
        215.0         32.0          5.34          0.26          8.69          0.38          None
        215.0         32.0          5.42          0.26          7.96          0.36          None
        215.0         32.0          5.51          0.27          7.16          0.34          None
        215.0         32.0          5.6           0.28          7.26          0.34          None
        215.0         32.0          5.69          0.28          6.02          0.31          None
        215.0         32.0          5.79          0.29          6.06          0.31          None
        215.0         32.0          5.88          0.3           6.03          0.31          None
        215.0         32.0          5.99          0.305         5.86          0.3           None
        215.0         32.0          6.09          0.31          5.16          0.28          None
        215.0         32.0          6.19          0.32          4.97          0.28          None
        215.0         32.0          6.3           0.33          4.88          0.27          None
        215.0         32.0          6.41          0.335         4.18          0.26          None
        215.0         32.0          6.53          0.345         4.0           0.25          None
        215.0         32.0          6.64          0.355         3.71          0.24          None
        215.0         32.0          6.76          0.365         3.61          0.24          None
        215.0         32.0          6.88          0.375         3.39          0.23          None
        215.0         32.0          7.01          0.385         2.86          0.22          None
        215.0         32.0          7.14          0.395         2.67          0.21          None
        215.0         32.0          7.28          0.405         2.57          0.21          None
        215.0         32.0          7.41          0.42          2.24          0.2           None
        215.0         32.0          7.55          0.43          2.22          0.2           None
        215.0         32.0          7.7           0.44          1.71          0.19          None
        215.0         32.0          7.85          0.46          1.9           0.19          None
        215.0         32.0          8.0           0.47          1.61          0.18          None
        215.0         32.0          8.16          0.48          1.35          0.17          None
        215.0         32.0          8.33          0.495         1.29          0.17          None
        215.0         32.0          8.5           0.515         1.0           0.16          None
        215.0         32.0          8.67          0.525         1.09          0.15          None
        215.0         32.0          8.85          0.545         0.87          0.15          None
        215.0         32.0          9.04          0.56          0.91          0.15          None
        215.0         32.0          9.23          0.58          0.49          0.14          None
        215.0         32.0          9.42          0.6           0.73          0.14          None
        215.0         32.0          9.62          0.62          0.4           0.14          None
        215.0         32.0          9.84          0.635         0.68          0.14          None
        215.0         32.0          10.06         0.655         0.48          0.13          None
        215.0         32.0          10.4          0.7           0.15          0.1           None
        215.0         32.0          10.88         0.725         0.3           0.09          None
        215.0         32.0          11.4          0.805         0.34          0.08          None
        215.0         32.0          11.94         0.865         0.09          0.11          None
        215.0         32.0          12.54         0.93          0.11          0.09          None
        215.0         32.0          13.18         0.995         0.05          0.16          None
        215.0         32.0          13.87         1.035         0.05          0.17          None          """
        self.assertTablesAlmostEqual(str(ds[('20576', '20576003', ' ')]).strip(), answer.strip())
        simple = ds[('20576', '20576003', ' ')].getSimplified()
        simpleAnswer = """#  Authors:   H.Knitter
#  Title:     -Measurement Of The Energy Spectrum Of Prompt Neutrons From The Fission Of Pu239 By 0.215 Mev Neutrons-
#  Year:      1975
#  Institute: Inst. for Ref. Mat. and Meas. (IRNM), Geel
#  Reference: Atomkernenergie 26, 76 (1975)
#  Subent:    20576003
#  Reaction:  Relative data  for 239Pu(n,Fission) Reference quantity not given
#        EN            EN-RSL        E             E-RSL         DATA          DATA-ERR      ERR-1
#        KEV           KEV           MEV           MEV           ARB-UNITS     ARB-UNITS     PER-CENT
        215.0         32.0          0.28          0.01          66.8          2.5           2.0
        215.0         32.0          0.31          0.01          70.2          2.4           2.0
        215.0         32.0          0.34          0.01          65.1          2.2           2.0
        215.0         32.0          0.36          0.01          70.5          2.2           2.0
        215.0         32.0          0.39          0.01          68.8          2.1           2.0
        215.0         32.0          0.41          0.01          74.2          2.1           2.0
        215.0         32.0          0.44          0.01          75.6          2.2           2.0
        215.0         32.0          0.46          0.01          74.8          2.1           2.0
        215.0         32.0          0.49          0.01          74.8          2.1           2.0
        215.0         32.0          0.51          0.01          73.6          2.0           2.0
        215.0         32.0          0.54          0.01          74.2          2.0           2.0
        215.0         32.0          0.56          0.01          75.7          2.0           2.0
        215.0         32.0          0.59          0.01          75.8          2.0           2.0
        215.0         32.0          0.61          0.01          76.6          2.1           2.0
        215.0         32.0          0.63          0.01          75.4          2.0           2.0
        215.0         32.0          0.66          0.01          78.7          2.1           2.0
        215.0         32.0          0.69          0.01          76.3          2.0           2.0
        215.0         32.0          0.71          0.01          78.6          2.1           2.0
        215.0         32.0          0.73          0.01          74.6          2.1           2.0
        215.0         32.0          0.76          0.01          78.7          2.0           2.0
        215.0         32.0          0.79          0.02          79.4          2.1           2.0
        215.0         32.0          0.81          0.02          78.3          2.1           2.0
        215.0         32.0          0.84          0.02          76.6          2.0           2.0
        215.0         32.0          0.86          0.02          80.0          2.2           2.0
        215.0         32.0          0.89          0.02          81.0          2.1           2.0
        215.0         32.0          0.91          0.02          80.2          2.1           2.0
        215.0         32.0          0.94          0.02          79.5          2.1           2.0
        215.0         32.0          0.96          0.02          78.4          2.1           2.0
        215.0         32.0          0.98          0.02          77.8          2.1           2.0
        215.0         32.0          1.01          0.02          76.8          2.2           2.0
        215.0         32.0          1.04          0.02          78.4          2.0           2.0
        215.0         32.0          1.06          0.02          78.3          2.2           2.0
        215.0         32.0          1.09          0.02          77.8          2.1           2.0
        215.0         32.0          1.11          0.02          74.9          2.1           2.0
        215.0         32.0          1.13          0.03          75.1          2.1           2.0
        215.0         32.0          1.16          0.03          76.0          2.1           2.0
        215.0         32.0          1.19          0.03          76.1          2.1           2.0
        215.0         32.0          1.21          0.03          74.0          2.0           2.0
        215.0         32.0          1.24          0.03          73.5          2.2           2.0
        215.0         32.0          1.26          0.03          76.7          1.6           2.0
        215.0         32.0          1.29          0.03          74.5          1.6           2.0
        215.0         32.0          1.32          0.03          72.3          1.5           2.0
        215.0         32.0          1.35          0.03          72.8          1.5           2.0
        215.0         32.0          1.39          0.04          72.2          1.5           2.0
        215.0         32.0          1.42          0.04          72.1          1.5           2.0
        215.0         32.0          1.45          0.04          69.1          1.7           2.0
        215.0         32.0          1.47          0.04          70.7          1.8           2.0
        215.0         32.0          1.5           0.04          71.3          1.8           2.0
        215.0         32.0          1.52          0.04          67.3          1.7           2.0
        215.0         32.0          1.55          0.04          68.4          1.7           2.0
        215.0         32.0          1.58          0.04          65.1          1.6           2.0
        215.0         32.0          1.6           0.04          65.7          1.6           2.0
        215.0         32.0          1.63          0.04          64.3          1.6           2.0
        215.0         32.0          1.66          0.05          64.1          1.6           2.0
        215.0         32.0          1.69          0.05          64.7          1.6           2.0
        215.0         32.0          1.72          0.05          61.9          1.5           2.0
        215.0         32.0          1.75          0.05          63.1          1.5           2.0
        215.0         32.0          1.79          0.05          63.0          1.5           2.0
        215.0         32.0          1.82          0.05          60.9          1.5           2.0
        215.0         32.0          1.85          0.05          59.9          1.5           2.0
        215.0         32.0          1.89          0.06          58.7          1.4           2.0
        215.0         32.0          1.93          0.06          58.0          1.4           2.0
        215.0         32.0          1.96          0.06          57.0          1.4           2.0
        215.0         32.0          2.0           0.06          56.1          1.4           2.0
        215.0         32.0          2.04          0.06          54.6          1.3           2.0
        215.0         32.0          2.07          0.06          54.1          1.8           2.0
        215.0         32.0          2.09          0.06          52.7          1.8           2.0
        215.0         32.0          2.11          0.07          52.0          1.8           2.0
        215.0         32.0          2.14          0.07          51.6          1.8           2.0
        215.0         32.0          2.16          0.07          52.9          1.8           2.0
        215.0         32.0          2.18          0.07          51.0          1.7           2.0
        215.0         32.0          2.2           0.07          51.0          1.7           2.0
        215.0         32.0          2.22          0.07          49.6          1.7           2.0
        215.0         32.0          2.25          0.07          48.9          1.7           2.0
        215.0         32.0          2.27          0.07          47.3          1.6           2.0
        215.0         32.0          2.29          0.07          49.5          1.7           2.0
        215.0         32.0          2.32          0.07          46.6          1.6           None
        215.0         32.0          2.34          0.07          45.4          1.6           None
        215.0         32.0          2.37          0.08          46.2          1.6           None
        215.0         32.0          2.39          0.08          46.6          1.6           None
        215.0         32.0          2.42          0.08          45.3          1.5           None
        215.0         32.0          2.44          0.08          44.0          1.5           None
        215.0         32.0          2.47          0.08          44.6          1.5           None
        215.0         32.0          2.5           0.08          41.6          1.4           None
        215.0         32.0          2.53          0.09          43.4          1.5           None
        215.0         32.0          2.56          0.09          41.3          1.4           None
        215.0         32.0          2.58          0.09          43.2          1.5           None
        215.0         32.0          2.61          0.09          41.4          1.4           None
        215.0         32.0          2.64          0.09          39.5          1.4           None
        215.0         32.0          2.67          0.09          38.9          1.3           None
        215.0         32.0          2.7           0.09          39.7          1.4           None
        215.0         32.0          2.73          0.1           37.5          1.3           None
        215.0         32.0          2.76          0.1           36.4          1.2           None
        215.0         32.0          2.79          0.1           36.1          1.2           None
        215.0         32.0          2.82          0.1           36.6          1.2           None
        215.0         32.0          2.86          0.1           36.2          1.2           None
        215.0         32.0          2.89          0.1           34.8          1.2           None
        215.0         32.0          2.93          0.1           34.0          1.2           None
        215.0         32.0          2.96          0.1           34.1          1.2           None
        215.0         32.0          3.0           0.11          33.4          1.2           None
        215.0         32.0          3.03          0.11          31.2          1.1           None
        215.0         32.0          3.07          0.11          32.4          1.1           None
        215.0         32.0          3.11          0.11          31.5          1.1           None
        215.0         32.0          3.15          0.12          30.7          1.1           None
        215.0         32.0          3.18          0.12          29.3          1.0           None
        215.0         32.0          3.22          0.12          28.6          1.0           None
        215.0         32.0          3.26          0.12          28.3          1.0           None
        215.0         32.0          3.3           0.12          27.1          1.0           None
        215.0         32.0          3.34          0.13          27.6          1.0           None
        215.0         32.0          3.39          0.13          26.3          0.9           None
        215.0         32.0          3.43          0.13          25.4          0.9           None
        215.0         32.0          3.48          0.14          24.6          0.9           None
        215.0         32.0          3.52          0.14          24.4          0.9           None
        215.0         32.0          3.57          0.14          23.7          0.8           None
        215.0         32.0          3.61          0.14          22.4          0.8           None
        215.0         32.0          3.66          0.15          21.7          0.8           None
        215.0         32.0          3.71          0.15          22.5          0.8           None
        215.0         32.0          3.76          0.15          21.1          0.8           None
        215.0         32.0          3.81          0.155         20.0          0.7           None
        215.0         32.0          3.86          0.155         19.0          0.7           None
        215.0         32.0          3.92          0.165         19.4          0.7           None
        215.0         32.0          3.97          0.165         17.7          0.7           None
        215.0         32.0          4.03          0.165         18.0          0.7           None
        215.0         32.0          4.08          0.175         16.6          0.6           None
        215.0         32.0          4.14          0.175         16.7          0.6           None
        215.0         32.0          4.2           0.18          16.0          0.6           None
        215.0         32.0          4.26          0.185         15.3          0.6           None
        215.0         32.0          4.32          0.185         15.2          0.6           None
        215.0         32.0          4.38          0.195         14.5          0.6           None
        215.0         32.0          4.45          0.195         13.2          0.5           None
        215.0         32.0          4.51          0.2           13.2          0.5           None
        215.0         32.0          4.57          0.205         13.1          0.5           None
        215.0         32.0          4.64          0.21          12.4          0.5           None
        215.0         32.0          4.72          0.215         12.3          0.5           None
        215.0         32.0          4.79          0.22          11.3          0.5           None
        215.0         32.0          4.86          0.225         10.8          0.4           None
        215.0         32.0          4.94          0.23          9.73          0.42          None
        215.0         32.0          5.01          0.235         10.0          0.4           None
        215.0         32.0          5.09          0.24          9.56          0.41          None
        215.0         32.0          5.17          0.245         8.77          0.39          None
        215.0         32.0          5.25          0.25          8.61          0.38          None
        215.0         32.0          5.34          0.26          8.69          0.38          None
        215.0         32.0          5.42          0.26          7.96          0.36          None
        215.0         32.0          5.51          0.27          7.16          0.34          None
        215.0         32.0          5.6           0.28          7.26          0.34          None
        215.0         32.0          5.69          0.28          6.02          0.31          None
        215.0         32.0          5.79          0.29          6.06          0.31          None
        215.0         32.0          5.88          0.3           6.03          0.31          None
        215.0         32.0          5.99          0.305         5.86          0.3           None
        215.0         32.0          6.09          0.31          5.16          0.28          None
        215.0         32.0          6.19          0.32          4.97          0.28          None
        215.0         32.0          6.3           0.33          4.88          0.27          None
        215.0         32.0          6.41          0.335         4.18          0.26          None
        215.0         32.0          6.53          0.345         4.0           0.25          None
        215.0         32.0          6.64          0.355         3.71          0.24          None
        215.0         32.0          6.76          0.365         3.61          0.24          None
        215.0         32.0          6.88          0.375         3.39          0.23          None
        215.0         32.0          7.01          0.385         2.86          0.22          None
        215.0         32.0          7.14          0.395         2.67          0.21          None
        215.0         32.0          7.28          0.405         2.57          0.21          None
        215.0         32.0          7.41          0.42          2.24          0.2           None
        215.0         32.0          7.55          0.43          2.22          0.2           None
        215.0         32.0          7.7           0.44          1.71          0.19          None
        215.0         32.0          7.85          0.46          1.9           0.19          None
        215.0         32.0          8.0           0.47          1.61          0.18          None
        215.0         32.0          8.16          0.48          1.35          0.17          None
        215.0         32.0          8.33          0.495         1.29          0.17          None
        215.0         32.0          8.5           0.515         1.0           0.16          None
        215.0         32.0          8.67          0.525         1.09          0.15          None
        215.0         32.0          8.85          0.545         0.87          0.15          None
        215.0         32.0          9.04          0.56          0.91          0.15          None
        215.0         32.0          9.23          0.58          0.49          0.14          None
        215.0         32.0          9.42          0.6           0.73          0.14          None
        215.0         32.0          9.62          0.62          0.4           0.14          None
        215.0         32.0          9.84          0.635         0.68          0.14          None
        215.0         32.0          10.06         0.655         0.48          0.13          None
        215.0         32.0          10.4          0.7           0.15          0.1           None
        215.0         32.0          10.88         0.725         0.3           0.09          None
        215.0         32.0          11.4          0.805         0.34          0.08          None
        215.0         32.0          11.94         0.865         0.09          0.11          None
        215.0         32.0          12.54         0.93          0.11          0.09          None
        215.0         32.0          13.18         0.995         0.05          0.16          None
        215.0         32.0          13.87         1.035         0.05          0.17          None          """
        self.assertTablesAlmostEqual(str(simple).strip(), simpleAnswer.strip())

    def test_spectrum_ave_cs(self):
        pass

    def test_resonance_int_cs(self):
        pass

    def test_targ_reaction_pol_quant_query(self):
        return
        # entmap = self.dbMgr.retrieve( target = 'H-1', reaction = 'D,EL', quantity = 'POL/DA' )
        flist = []
        entmap = self.dbMgr.retrieve(target="PU-239", reaction="N,F", quantity="SIG", rawEntry=True)
        for e in entmap:
            ent = exfor_entry.X4Entry(entmap[e])
            flist.append(e)
            for s in ent:
                if 'REACTION' in ent[s]['BIB']:
                    for r in ent[s]['BIB']['REACTION']:
                        didreaction = False
                        for r in ent[s]['BIB']['REACTION'].reactions:
                            qlist = ent[s]['BIB']['REACTION'].reactions[r][0].quantity
                            if 'EVAL' not in qlist and 'REL' not in qlist and qlist != 'Coupled' and 'DERIV' not in qlist:
                                if qlist in [['SIG'], ['PAR', 'SIG'], ['WID'], ['EN'], ['SIG', 'RES']]: continue
                                if not didreaction:
                                    # print s,repr(ent[ s ][ 'BIB' ][ 'REACTION' ]),
                                    print(s, str(ent[s]['BIB']['REACTION']))
                                    didreaction = False
                                print('   ', qlist)
        print(' '.join(['X4all/' + x[:-2] + '/' + x + '.x4' for x in flist]))


if __name__ == "__main__":
    # try:
    #     import xmlrunner
    #
    #     unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-results'))
    # except ImportError:
    unittest.main()
    print()
    print()
