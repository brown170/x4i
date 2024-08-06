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
import zipfile
import datetime
from x4i.exfor_paths import DATAPATH


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
DEFAULTEXFORSOURCE = 'NDS-git'


__doc__ = """
Install EXFOR data files from one of the varients of the EXFOR Master file or in development NRDC EXFOR git projects.
"""


# ------------------------------------------------------------------------------
#                            .... ARGPARSE ....
# ------------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', dest='verbose', default=False, action='store_true', help="Enable verbose output.")
    parser.add_argument('--source', choices=EXFORSOURCES.keys(), default=DEFAULTEXFORSOURCE,
                        help="Output format (Default: %s)" % DEFAULTEXFORSOURCE)
    parser.add_argument('--skip-download', default=False, action='store_true',
                        help="Skip downloading from data source (i.e., you already have it for some reason)")
    parser.add_argument('--skip-indexing', default=False, action='store_true', 
                        help="Skip indexing the data (i.e., you want to somehow do it separately)")
    parser.add_argument("--db", default=DATAPATH+os.sep+"db", help="Location of local EXFOR data files (Default %s)" % (DATAPATH+os.sep+"db"))
    return parser.parse_args()


# ------------------------------------------------------------------------------
#                            .... UTILITIES ....
# ------------------------------------------------------------------------------
def archive_metadata(_datapath, _metadata):
    fname = DATAPATH+os.sep+"database_info.json"
    # remove old file
    if os.path.exists(fname):
        os.remove(fname)
    # save new data
    with open(fname, mode='w') as jsonfile:
        json.dump(_metadata, jsonfile)


# ------------------------------------------------------------------------------
#                            .... MAIN ....
# ------------------------------------------------------------------------------

def main():
    args = parse_args()

    # Metadata about this data source download
    metadata = {}
    metadata.update(EXFORSOURCES[args.source])

    # Remove old database (link)
    if os.path.exists(args.db):
        os.unlink(args.db) 

    if not args.skip_download:
        if EXFORSOURCES[args.source]['mode'] == 'git':
            # pull head from github repo
            subprocess.run(["git", 'clone', '--depth', '1', EXFORSOURCES[args.source]['url']], cwd=DATAPATH)

        elif EXFORSOURCES[args.source]['mode'] == 'zip':
            with tempfile.NamedTemporaryFile(delete=False, dir=DATAPATH) as tmp_file:
                # download file from NRDC page
                with urllib.request.urlopen(
                        urllib.request.Request(
                            EXFORSOURCES[args.source]['url'], 
                            {}, 
                            {'User-Agent': "x4i"})) as response:
                    shutil.copyfileobj(response, tmp_file)
                    # unpack zipfile
                    with zipfile.ZipFile(tmp_file) as zf:
                        zf.extractall(path=DATAPATH)
                # clean up
                if os.path.exists(tmp_file.name):
                    os.remove(tmp_file.name)
        else:
            raise ValueError("EXFOR source %s unknown" % args.source)

    # link right place to "db"
    os.symlink(DATAPATH + os.sep + EXFORSOURCES[args.source]['relative_data_path'], args.db)

    # save the metadata about this download
    metadata['downloaded'] = str(datetime.datetime.now())
    archive_metadata(DATAPATH, metadata)

    # Rebuild index
    if not args.skip_indexing:
        if args.source != "NDS-git":
            raise NotImplementedError("Only the default option is currently coded")
        if args.verbose:
            subprocess.run(["setup-exfor-db-index.py", "-v"])
        else:
            subprocess.run(["setup-exfor-db-index.py"])


if __name__ == "__main__":
    main()