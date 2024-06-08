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
#   0.     Rework imports for Python3.X compatibility (David Brown <dbrown@bnl.gov>, 2018-12-04T18:09:02)
#
################################################################################

from os import sep, path

# Common filenames
indexFileName = 'index.tbl'
dictionaryFileName = 'dictionaries.tbl'
doiFileName = 'doi.tbl'
errorFileName = 'error-entries.pickle'
coupledFileName = 'coupled-entries.pickle'
monitoredFileName = 'monitored-entries.pickle'
reactionCountFileName = 'reaction-count.pickle'
dbZipFileName = 'exfor-current.zip'
dbPath = 'db'

__path__ = path.split(__file__)[0]

# Paths for standard usage
DATAPATH = sep.join([__path__, 'data'])
DICTPATH = sep.join([__path__, 'dicts'])
fullIndexFileName = DATAPATH + sep + indexFileName
fullDictionaryFileName = DATAPATH + sep + dictionaryFileName
fullDoiFileName = DATAPATH + sep + doiFileName
fullErrorFileName = DATAPATH + sep + errorFileName
fullCoupledFileName = DATAPATH + sep + coupledFileName
fullMonitoredFileName = DATAPATH + sep + monitoredFileName
fullReactionCountFileName = DATAPATH + sep + reactionCountFileName
fullDBZipFileName = DATAPATH + sep + dbZipFileName
fullDBPath = DATAPATH + sep + dbPath
