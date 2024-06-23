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

from setuptools import setup
import os

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
    scripts = ["bin/setup-exfor-db-index.py", "bin/get-exfor-entry.py", 'bin/install-exfor-db.py'],
    license = open( 'LICENSE.txt' ).read(),
    description = 'A "simple" python interface to the EXFOR library',
    long_description = open( 'README.md' ).read()
)
