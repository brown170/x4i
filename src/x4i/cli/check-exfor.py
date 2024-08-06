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
#   0.     New file
#
################################################################################
import os
import argparse
from x4i import exfor_entry, exfor_manager

def process_args():
    parser = argparse.ArgumentParser(description = 'Get an EXFOR entry')
    parser.set_defaults( verbose = True )
    parser.add_argument("-v", action="store_true", dest='verbose', help="enable verbose output")
    parser.add_argument("-q", action="store_false", dest='verbose', help="disable verbose output")
    parser.add_argument("file", type=str, help="Check this EXFOR file" )
    parser.add_argument('--entry', type=str, default=None, help="Entry in the file to check")
    return parser.parse_args()

if __name__ == "__main__":
    args = process_args()

    # Get the ENTRY/SUBENTRY requested
    if args.entry is not None: 
        entry = args.entry
    else:
        entry = args.file.split(os.sep)[-1].split('.')[0]
    if args.verbose:
        print("Reading entry %s from file %s" % (entry, args.file))
    searchResult = exfor_entry.x4EntryFactory( entry, filePath=args.file)

    # Inventory of SUBENTS
    if args.verbose:
        print('Set has these SUBENTS:', list(searchResult.keys()))
        for k in searchResult.keys():
            print('   ','SUBENT %s has these sections:' % k, list(searchResult[k].keys()))

    # Attempt simplification on each subentry & dataset
    print('Attempting simplification')            
    ds = searchResult.getSimplifiedDataSets()
    for kk in ds:
        if ds[kk].simplified and args.verbose:
            print('   ','Simplification of set', kk, 'successful')
        if not ds[kk].simplified:
            print('   ','Simplification of set', kk, 'FAILED')



