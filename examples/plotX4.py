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
#   1. Update for Python3.X compaibility (D. Brown <dbrown@bnl.gov>, 9 Nov 2018)
#   2. Add controls to set path to Grace executable (D. Brown <dbrown@bnl.gov>, 9 Nov 2018)
#   3. Update code to use simplified retrieve function (D. Brown <dbrown@bnl.gov>, 18 Dec 2017)
#
################################################################################
from __future__ import print_function

import sys, os
sys.path.append( '..' )
from x4i import exfor_manager, exfor_entry

GRACE=os.environ.get("GRACE", 'xmgrace')

isotope  = 'AS-75' #'AL-27'
reaction = 'N,2N'
observable = 'CS'
outtype = 'PostScript'

if __name__ == "__main__":

    try: isotope = sys.argv[1].upper()
    except: pass
    try: reaction = sys.argv[2].upper()
    except: pass

    title = isotope.capitalize() + '(' + reaction.lower()
    outfile = '"' + title + ')' + '.' + outtype.lower() + '"'

    db = exfor_manager.X4DBManagerPlainFS( )

    fileList = []
    i = 0
    subents = db.retrieve( target = isotope, reaction = reaction, quantity = observable )
    print('Retrieving entries:')
    for e in subents:
        print('    Entry:',e)
        try:
            if isinstance( subents[ e ], exfor_entry.X4Entry ):
                ds = subents[ e ].getSimplifiedDataSets( makeAllColumns = True )
        except KeyError:
            print("Got KeyError on entry", e, "ignoring")
            print(subents[ e ].keys())
            continue
        for d in ds:
            print('       ',d)
            result = str( ds[ d ] )
            fileList.append( 'junk' + str( i ) + '.dat' )
            open( fileList[-1], mode='w' ).writelines( result )
            i += 1
    if i == 0: sys.exit(1)
    command = GRACE+' -autoscale xy -hardcopy -remove -printfile ' \
        + outfile+ ' -hdevice ' + outtype + ' '\
        + ' '.join( [ '-settype xydxdy '+fname for fname in fileList ] ) \
        + ' -saveall ' + outfile.replace( outtype.lower(), 'agr' )
    print(command)
    os.system( command )
    os.system( 'rm -f '+' '.join( fileList ) )
