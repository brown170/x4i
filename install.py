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
import tempfile
import shutil
import urllib.request
import json


EXFORZIP=None #"X4-2021-03-08.zip"
EXFORURL=None #"https://www-nds.iaea.org/exfor-master/x4toc4/%s"%EXFORZIP


with open("x4i/data/database_info.json") as jsonfile:
    jsondata = json.load(jsonfile)
    EXFORZIP = jsondata["zipfile"]
    EXFORURL = jsondata["url"] + EXFORZIP

with urllib.request.urlopen(urllib.request.Request(EXFORURL, {}, {'User-Agent': "x4i"})) as response:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        shutil.copyfileobj(response, tmp_file)
subprocess.run(["bin/setup-exfor-db.py", "--x4c4-master", "%s"%tmp_file.name])
tmp_file.close()
if os.path.exists(tmp_file.name):
    os.remove(tmp_file.name)
