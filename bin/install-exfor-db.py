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
#   1.     Add shebang (David Brown <dbrown@bnl.gov>, 2021-06-16T08:16:09)
#   2.     python -> $PYTHON (David Brown <dbrown@bnl.gov>, 2021-06-16T08:15:48)
#
################################################################################

#
#
#  USE THIS CODE TO DOWNLOAD AND INSTALL CORRECT
#  IAEA DATABASE FOR EDITABLE OR DEVELOPER INSTALLS
#
#
import os
import subprocess
import argparse
import tempfile
import shutil
import urllib.request
import json


EXFORSOURCES = {
    "NDS-git": {
        "url": "https://github.com/IAEA-NDS/exfor_master.git",
	    "mode": "git",
        "relative_data_path": "exfor_master/exforall/"},
    "NRDC-git": {
        "url": "https://github.com/IAEA-NRDCNetwork/EXFOR-Archive.git",
	    "mode": "git",
	    "relative_data_path": "EXFOR-Archive/EXFOR/"},
    "EXFOR-Master": {	
        "url": "https://www-nds.iaea.org/nrdc/exfor-master/entry/entry.zip",
	    "mode": "zip",
	    "relative_data_path": "entry/"}}

#	- commit_hash = ...get the hash...
#	- sha = ...get the hash...
#	- downloaded = ...get the datetime...

__doc__ = """
"""


# ------------------------------------------------------------------------------
#                            .... ARGPARSE ....
# ------------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', dest='verbose', default=False, action='store_true', help="Enable verbose output.")
    parser.add_argument('-o', dest='outFile', default="out.csv", help="Save to this file")
    parser.add_argument('--rxn', choices=[x.name for x in list(ienums.Reaction)], default='capture',
                        help='Reaction to retrieve (Default: capture)')
    parser.add_argument('--format', choices=['csv', 'tex', 'png', 'json', 'html'], default='csv',
                        help="Output format (Default: csv)")
    parser.add_argument('--skipBeta', action='store_true', default=False,
                        help="Skip the pre-computed beta version of ENDF")
    parser.add_argument('--inter', dest='interJSON', default=None, type=str,
                        help='Output file from inter.py, in JSON format (Default: None)')
    parser.add_argument('iso', type=str, help='Isotope name in GNDS format (Examples: U235, Br, Al26_m1)')
    return parser.parse_args()


# ------------------------------------------------------------------------------
#                            .... MAIN ....
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Command line parsing
    args = parse_args()

    EXFORZIP=None #"X4-2021-03-08.zip"
    EXFORURL=None #"https://www-nds.iaea.org/exfor-master/x4toc4/%s"%EXFORZIP


    with open("x4i/data/database_info.json") as jsonfile:
        jsondata = json.load(jsonfile)
        EXFORZIP = jsondata["zipfile"]
        EXFORURL = jsondata["url"] + EXFORZIP

    try:
        with urllib.request.urlopen(urllib.request.Request(EXFORURL, {}, {'User-Agent': "x4i"})) as response:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                shutil.copyfileobj(response, tmp_file)

    except Exception as ex:
        print("\n ERROR encountered while downloading the EXFOR database:\n  ", ex)
        print(f"""\n\nAs an alternative, please manually download the database zip file from {EXFORURL},
    place it in the x4i directory and issue the following command (this takes a while):

    ./bin/setup-exfor-db.py --x4c4-master {EXFORZIP}

    Once that command finishes, {EXFORZIP} can be safely deleted.""")

    else:
        subprocess.run(["bin/setup-exfor-db.py", "--x4c4-master", "%s"%tmp_file.name])
        tmp_file.close()
        if os.path.exists(tmp_file.name):
            os.remove(tmp_file.name)
