#! /usr/bin/env python

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
#   0.     Python3.X compatibility  (David Brown <dbrown@bnl.gov>, 2018-11-16T19:46:51)
#   1.     more options for data & doc display (David Brown <dbrown@bnl.gov>, 2013-06-19T14:16:24)
#   2.     strip out subents we aren't interested in (David Brown <dbrown@bnl.gov>, 2013-06-19T13:25:19)
#   3.     making sure the file behavior and the db behavior are the same (David Brown <dbrown@bnl.gov>, 2013-06-19T12:27:26)
#   4.     now use x4EntryFactory (David Brown <dbrown@bnl.gov>, 2013-06-19T12:20:02)
#   5.     switch file reads to use universal newline mode to correct bug with missing (yet important) black lines (David Brown <dbrown@bnl.gov>, 2013-06-18T21:00:59)
#   6.     tweak so display of info and raw data not mutually exclusive (David Brown <dbrown@bnl.gov>, 2013-06-18T12:38:37)
#   7.     rework code to make file specification easier for testing (David Brown <dbrown@bnl.gov>, 2013-06-18T11:56:36)
#   8.     better name (David Brown <dbrown@bnl.gov>, 2012-07-24T13:17:21)
#
################################################################################

import argparse
from x4i import exfor_entry, exfor_manager

def process_args():
    parser = argparse.ArgumentParser(description = 'Get an EXFOR entry')
    parser.set_defaults( verbose = True )
    parser.add_argument("-v", action="store_true", dest='verbose', help="enable verbose output")
    parser.add_argument("-q", action="store_false", dest='verbose', help="disable verbose output")
    parser.add_argument("-s", dest="subent", default=None, type=str, help="Subentry to retrieve" )
    parser.add_argument("-e", dest="ent", default=None, type=str, help="Entry to examine: prints out the SUBENTs" )
    parser.add_argument("-f", dest="file", default=None, type=str, help="Don't use the exfor_manager.X4DBManager, just grab from the file directly.  The file name is the argument of -f" )
    parser.add_argument("--raw", default=False, dest="raw", action="store_true", help="Get raw EXFOR file, don't translate" )
    parser.add_argument("--rawdata", default=False, dest="rawdata", action="store_true", help="Extract raw form of data in EXFOR data" )
    parser.add_argument("--data", default=False, dest="data", action="store_true", help="Extract simple form of data in EXFOR data" )
    parser.add_argument("--rawdoc", default=False, dest="rawdoc", action="store_true", help="Extract documentation from an EXFOR SUBENT" )
    parser.add_argument("--doc", default=False, dest="doc", action="store_true", help="Interpreted documentation from an EXFOR SUBENT" )
    parser.add_argument("--nada", default=False, dest="nada", action="store_true", help="Don't actually do anything with the SUBENT" )
    return parser.parse_args()

if __name__ == "__main__":
    args = process_args()
    if args.subent == None and args.ent == None:
        raise ValueError("No ENTRY or SUBENT specified")
    if args.subent != None and len( args.subent ) != 8: 
        raise ValueError( "SUBENT must have 8 characters" )
    if args.ent != None and len( args.ent ) != 5: 
        raise ValueError( "ENTRY must have 5 characters, have '%s'" % args.ent )

    # Get the ENTRY/SUBENTRY requested
    if not args.file:
        dbMgr = exfor_manager.X4DBManagerPlainFS( )
        if args.ent != None:    searchResult = dbMgr.retrieve( ENTRY = args.ent, rawEntry=args.raw )
        else:                   searchResult = dbMgr.retrieve( SUBENT = args.subent, rawEntry=args.raw  )
    else:
        searchResult = exfor_entry.x4EntryFactory( args.ent, filePath=args.file, rawEntry=args.raw )
        if args.subent != None: # must filter
            if args.raw: pass
            else:
                if args.subent not in searchResult[ theEntry ]: raise KeyError( "SUBENT "+args.subent+" not found!" )
                for k in list(searchResult[ theEntry ].keys()):
                    if k.endswith( '001' ) or k == args.subent: continue
                    del( searchResult[ theEntry ][k] )

    print(searchResult)

    # Just print out the SUBENT keys
    if args.ent != None:
        print("This ENTRY:      ", list(searchResult.keys())[0])
        for i in searchResult[ list(searchResult.keys())[0] ]:
            print("   ", i.split('\n')[0][0:22])

    # Examine a SUBENT
    if args.subent != None:
        subent = searchResult
        keys = list(searchResult.keys())
        keys.sort()
        if not args.nada:
            if args.raw:
                print('\n\n')
                for k in keys: print('\n'.join( searchResult[k] ) )
            if args.rawdoc:
                print('\n\n')
                print(repr(searchResult[keys[0]][1]))
            if args.doc:
                print('\n\n')
                print(searchResult[keys[0]][1])
            if args.rawdata:
                if args.subent.endswith( '001' ): raise ValueError( "Documentation SUBENTs (those ending in '001') do not have DATA sections" )
                print(10*'-','Raw Data',10*'-')
                print(searchResult[keys[-1]][args.subent]['DATA'])
                print(10*'-','Errors',10*'-')
                print(searchResult[keys[-1]].errors)
            if args.data:
                if args.subent.endswith( '001' ): raise ValueError( "Documentation SUBENTs (those ending in '001') do not have DATA sections" )
                print(10*'-','Data',10*'-')
                print(searchResult[keys[-1]].getDataSets())
                print(10*'-','Errors',10*'-')
                print(searchResult[keys[-1]].errors)
