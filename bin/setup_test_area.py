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
#
################################################################################
#
# Changes since LLNL release (x4i-1.0):
#
#   0.     Python 3.X compatibilty (David Brown <dbrown@bnl.gov>, 2018-11-16T19:46:51)
#   1.     Set up test db (David Brown <dbrown@bnl.gov>, 2014-02-04T17:31:59)
#
################################################################################
from __future__ import print_function
import os, shutil
theEntries = '''
E0783
10001
13787
14129
21971
20795
13883
10036
10135
10149
10187
10241
10275
10315
10316
10355
10592
10804
10862
10892
10903
11036
11042
11055
11066
11069
11072
11078
11079
11083
11084
11090
11096
11109
11117
11123
11124
11128
11129
11131
11167
12643
12656
12780
12884
12909
12917
13150
13623
13782
13793
13795
13986
14017
14160
20287
20296
20319
20360
20389
20404
20778
20964
21223
21365
21367
21790
21795
21800
21815
21852
21985
21993
22207
22223
22225
22277
22542
22668
22831
22886
22914
22949
30078
30162
30327
30340
30679
31048
41202
41206
41207
41209
41224
41530
C0606
C0801
C1236
C1285
C1560
D0480
E0783
E0811
E0839
E1627
E1723
E1772
E1907
11321
11314
13883
20576
12326
E0783
E2008
E2052
E2159
E2346
O1434
O1664
O1732
O1974
E0783
13883
21971
20795
14129
11321
11321
11314
11314
12326
20576
12326
20576
40121
40177
40431
41335
'''
originals = 'x4i/data_bk/db'
copyTo = 'x4i/data/db'
for f in theEntries.strip().split('\n'):
    if os.path.exists( originals+os.sep+f[0:3]+os.sep+f+'.x4'):
        print("copying", f )
        if not os.path.exists(copyTo+os.sep+f[0:3]): os.makedirs(copyTo+os.sep+f[0:3])
        shutil.copy(originals+os.sep+f[0:3]+os.sep+f+'.x4', copyTo+os.sep+f[0:3]+os.sep+f+'.x4' )
    else:
        print("can't find",f)
