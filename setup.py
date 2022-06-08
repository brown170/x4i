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
#   0.     Change README.txt to README.md (David Alan Brown <dbrown@bnl.gov>, 2020-02-14T14:12:13)
#   1.     Improved install, license readability and new version number (David Brown <dbrown@bnl.gov>, 2019-08-14T19:00:24)
#   2.     Python3.X compatibility (David Brown <dbrown@bnl.gov>, 2018-11-16T21:37:15)
#   3.     Get rid of old, unneeded continuation markers (David Brown <dbrown@bnl.gov>, 2018-11-16T19:48:12)
#   4.     Bump the revision number again (David Brown <dbrown@bnl.gov>, 2014-09-08T14:16:56)
#   5.     Fix install of doc & test data (David Brown <dbrown@bnl.gov>, 2014-09-08T13:39:57)
#   6.     Add test/ stuff to project (David Brown <dbrown@bnl.gov>, 2014-02-13T20:02:15)
#   7.     Up the version number (David Brown <dbrown@bnl.gov>, 2012-11-04T19:54:42)
#   8.     Fix a path (David Brown <dbrown@bnl.gov>, 2012-07-24T15:35:01)
#
################################################################################

from distutils.core import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
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


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        print("X4i is rebuilding the EXFOR index.\n-->THIS WILL TAKE A LONG TIME, DON'T END THE PROCESS!! Just go get a snack.")
        install.run(self)

        # Get the version of EXFOR that we've been using for a while
        # this could be done way better with SHA hash checking, log files & stuff and
        # be part of setup-exfor-db.py.
        with urllib.request.urlopen(urllib.request.Request(EXFORURL, {}, {'User-Agent': "x4i"})) as response:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                shutil.copyfileobj(response, tmp_file)
        subprocess.run(["bin/setup-exfor-db.py", "--x4c4-master", "%s"%tmp_file.name])
        tmp_file.close()
        if os.path.exists(tmp_file.name):
            os.remove(tmp_file.name)


setup(
    name = 'x4i',
    version = '1.0.4',
    author = 'David A. Brown',
    author_email = 'dbrown@bnl.gov',
    packages = [ 'x4i', 'x4i.test' ],
    package_data = {
        'x4i': [
            os.sep.join( [ 'dicts', '*.txt' ] ),
            os.sep.join( [ 'data', '*.t*' ] ),
            os.sep.join( [ 'data', '*.pickle' ] ),
            os.sep.join( [ 'data', 'db', '*', '*.x4' ] ) ],
        'x4i.test': [
            '*.x4',
            os.sep.join( [ 'data', '*.t*' ] ),
            os.sep.join( [ 'data', '*.pickle' ] ),
            os.sep.join( [ 'data', 'db', '*', '*.x4' ] ) ] },
    url = 'https://github.com/brown170/x4i',
    scripts = ["bin/setup-exfor-db.py", "bin/get-entry.py"],
    license = open( 'LICENSE.txt' ).read(),
    description = 'A "simple" python interface to the EXFOR library',
    long_description = open( 'README.md' ).read(),
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
)
