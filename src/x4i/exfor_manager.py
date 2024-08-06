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
#   0.     Add as_JSON argument for retrieve(); PEP-8 compliance (David Brown <dbrown@bnl.gov>, 2021-09-10T21:19:37)
#   1.     New feature: can now query & retrieve via reference code (Sayers, Grier Idriss (gis7617) <gis7617@lockhaven.edu>, 2019-08-04T13:26:56)
#   2.     Rework imports for Python3.X (David Brown <dbrown@bnl.gov>, 2018-12-04T18:09:02)
#   3.     Python3.X compatibility & PEP-8 compliance (David Brown <dbrown@bnl.gov>, 2018-12-04T17:44:23)
#   4.     Get rid of obsolete line continuation characters (David Brown <dbrown@bnl.gov>, 2017-12-21T16:22:47)
#   5.     Fix path bug introduced when trying to get the unit tests working (David Brown <dbrown@bnl.gov>, 2014-11-07T03:07:18)
#   6.     Rewire handling of path to data (David Brown <dbrown@bnl.gov>, 2014-09-15T14:35:20)
#   7.     Get rid of reference to obsolete database managers
#          Fix missing import in utilities (David Brown <dbrown@bnl.gov>, 2014-02-14T17:20:47)
#   8.     x4EntryFactory was returning the whole entry, not just the requested parts (David Brown <dbrown@bnl.gov>, 2013-10-10T15:45:12)
#   9.     Fix wiring if rawEntry=False (which is now the default)
#          Update unit tests (David Brown <dbrown@bnl.gov>, 2013-06-19T12:18:10)
#   10.    Streamline X4Entry initialization, hopefully also squashing bugs along the way (David Brown <dbrown@bnl.gov>, 2013-06-19T12:02:54)
#   11.    Switch file reads to use universal newline mode to correct bug with missing (yet important) black lines (David Brown <dbrown@bnl.gov>, 2013-06-18T21:00:59)
#   12.    Fix the paths and move them into the main module __ini__.py & tell exfor_manager about them (David Brown <dbrown@bnl.gov>, 2012-07-24T15:33:16)
#
################################################################################

# !/usr/bin/python
# module exfor_manager.py
"""
exfor_manager module - Classes and Methods to retrieve EXFOR Entries and SubEntries from the database
"""
import zipfile
from x4i.exfor_paths import DATAPATH, fullIndexFileName

from x4i.exfor_entry import x4EntryFactory
from x4i.exfor_utilities import *

EntryLetterConversion = {'10': 'A', '11': 'B', '12': 'C', '13': 'D', '14': 'E', '15': 'F', '16': 'G', '21': 'L',
                         '22': 'M', '24': 'O', '25': 'P', '27': 'R', '28': 'S', '29': 'T', '31': 'V'}
revEntryLetterConversion = {'A': '10', 'B': '11', 'C': '12', 'D': '13', 'E': '14', 'F': '15', 'G': '16', 'L': '21',
                            'M': '22', 'O': '24', 'P': '25', 'R': '27', 'S': '28', 'T': '29', 'V': '31'}


# -------------------------------------------
#
# X4DBManager
#
# -------------------------------------------
def decompress_entry(s):
    """Some databases zip the (Sub)Entries before storing them.  This routine unzips them."""
    open('davestmpfile.zip', mode='w').write(s[1])
    if not zipfile.is_zipfile('davestmpfile.zip'):
        raise Exception("Cannot decompress entry " + str(s[1]))
    news = (s[0], ''.join(os.popen('unzip -c davestmpfile.zip').readlines()[2:]))
    if os.path.exists(s[0] + '.txt'):
        os.remove(s[0] + '.txt')
    if os.path.exists('davestmpfile.zip'):
        os.remove('davestmpfile.zip')
    return news


def __fixkey__(i):
    """
    Checks the format of the key & converts it to a 5 or 8 character string for use in other classe.
    Don't use this directly!
    .
    Input:      i int or string, correpsonding to the EXFOR Accession Number, a 5 or 8 digit number (5 == Entry, 8 == SubEntry)
    Returns:    EXFOR Entry or SubEntry key, depending on number of digits in key (5 == Entry, 8 == SubEntry)
    """
    if type(i) != str:
        i = str(i)
    if len(i) not in [5, 8]:  # is an Entry or a SubEntry
        raise KeyError('Invalid Entry or SubEntry key')
    return i


class X4DBManager:
    """
    EXFOR data base manager base class
    This defines the API.

    As a user, you should use __init__ to establish the connection to your preferred database,
    then access data using the query, retrieve, __getitem__ and __contains__ member functions.

    All of the other member functions should only be needed by code developers.
    """

    def __init__(self, **kw):
        # ---- the Python connection and a cursor ----
        self.CONNECTION = None
        self.CURSOR = None

    def __getitem__(self, i):
        """
        Get an EXFOR Entry or SubEntry

        Input:      i int or string, corresponding to the EXFOR Accession Number,
                    a 5 or 8 digit number (5 == Entry, 8 == SubEntry)
        Returns:    EXFOR Entry or SubEntry string, depending on number of digits in key (5 == Entry, 8 == SubEntry)
        """
        i = __fixkey__(i)
        if len(i) == 5:
            return self.retrieve(ENTRY=i)
        return self.retrieve(SUBENT=i)

    def __setitem__(self, i):
        """
        Set an EXFOR Entry or SubEntry using Python assignment operator (=)

        Input:      i, int or string EXFOR Accession Number, a 5 or 8 digit number (5 == Entry, 8 == SubEntry)
        """
        i = __fixkey__(i)
        raise NotImplementedError("Do not use X4DBManager directly, use derived class")

    def __contains__(self, i):
        """
        Check whether an EXFOR Entry or SubEntry exists in the database

        Input:      i, int or string, EXFOR Accession Number, a 5 or 8 digit number (5 == Entry, 8 == SubEntry)
        Returns:    bool, whether an EXFOR Entry or SubEntry exists in the database
        """
        i = __fixkey__(i)
        if len(i) == 5:
            return len(self.query(ENTRY=i)) > 0
        return len(self.query(SUBENT=i) > 0)

    def run_sql_query(self, table, column, condition=None, VERBOSE=False):
        """
        Performs the actual SQL query, returns the number of results so you can request that
        many by calling CURSOR.fetchmany()
        """
        q = "select " + column + " from " + table
        if condition is not None:
            q += " where " + condition
        if VERBOSE:
            print(q)
        return self.CURSOR.execute(q)

    def query(self, author=None, reaction=None, target=None, projectile=None, quantity=None, product=None, MF=None,
              MT=None, C=None, S=None, I=None, SUBENT=None, ENTRY=None, POINTER=None):
        """Use this function to search for all (Sub)Entries matching criteria in query call.
        This function returns a dictionary with the following structure:
            { ENTRY#0:[ SUBENT001, SUBENT#1, SUBENT#2, ... ], ... }.
        Here ENTRY#0 is the entry number whose subentries match the query.  The SUBENT001 is the documentation
        subentry number, which is always included, and SUBENT#1, ... are the subentry numbers matching the search
        criteria."""
        raise NotImplementedError("Do not use X4DBManager directly, use derived class")

    def retrieve(self, author=None, reaction=None, target=None, projectile=None, quantity=None, product=None, MF=None,
                 MT=None, C=None, S=None, I=None, SUBENT=None, ENTRY=None, POINTER=None):
        """Execute a query, matching the criteria specified.
        This function returns a dictionary with the following structure:
            { ENTRY#0:[ SUBENT001, SUBENT#1, SUBENT#2, ... ], ... }.
        Here ENTRY#0 is the entry number whose subentries match the query.  The SUBENT001 is the documentation subentry
        itself, which is always included, and SUBENT#1, ... are the subentries themselves matching the search
        criteria."""
        raise NotImplementedError("Do not use X4DBManager directly, use derived class")


# -------------------------------------------
#
# X4DBManagerPlainFS
#
# -------------------------------------------
class X4DBManagerPlainFS(X4DBManager):
    """EXFOR data base manager for data stored on local filesystem in directory hierarchy."""

    def __init__(self, **kw):
        self.DATAPATH = kw.get('datapath', DATAPATH)
        self.database = kw.get('database', fullIndexFileName)
        X4DBManager.__init__(self, **kw)
        if 'database' in kw:
            del kw['database']
        if 'datapath' in kw:
            del kw['datapath']
        import sqlite3
        self.CONNECTION = sqlite3.connect(self.database, **kw)
        self.CURSOR = self.CONNECTION.cursor()

    def query(self, author=None, reaction=None, target=None, projectile=None, quantity=None, product=None, MF=None,
              MT=None, C=None, S=None, I=None, SUBENT=None, ENTRY=None, pointer=None, reference=None):
        """Use this function to search for all (Sub)Entries matching criteria in query call.
        This function returns a dictionary with the following structure:
            { ENTRY#0:[ SUBENT001, SUBENT#1, SUBENT#2, ... ], ... }.
        Here ENTRY#0 is the entry number whose subentries match the query.  The SUBENT001 is the documentation subentry
        number, which is always included, and SUBENT#1, ... are the subentry numbers matching the search criteria."""
        # handle the search criteria we aren't ready to use yet
        for key in ['projectile', 'product', 'MF', 'MT', 'C', 'S', 'I']:
            if eval(key) is not None:
                try:
                    raise NotImplementedError("Retrieval critria " + key + " not implemented yet")
                except NotImplementedError:
                    pass

        criteria = []

        # Search for matching authors
        if author is not None:
            criteria.append("author = '%s' " % author.capitalize())

        # Search for matching target
        if target is not None:
            criteria.append("target = '%s' " % target.upper())

        # Search for matching reaction
        if reaction is not None:
            criteria.append("reaction = '%s' " % reaction.upper())

        # Search for matching reaction
        if projectile is not None:
            criteria.append("projectile = '%s' " % projectile.upper())

        # Search for matching quantity
        if quantity is not None:
            if quantity == 'CS':
                criteria.append("quantity = '%s' " % "SIG")
            else:
                criteria.append("quantity = '%s' " % quantity.upper())

        # Search for matching SUBENTRY
        if SUBENT is not None:
            criteria.append("subent = '%s' " % SUBENT)

        # Search for matching ENTRY
        if ENTRY is not None:
            criteria.append("entry = '%s' " % ENTRY)

        # Search for matching POINTER
        if pointer is not None:
            criteria.append("pointer = '%s' " % pointer)

        if reference is not None:
            criteria.append("reference = '%s' " % reference)

        # Run the big query
        criteria = ' and '.join(criteria)
        if criteria != '':
            self.run_sql_query("theworks", "subent", criteria)
            result_list = unique([x[0] for x in self.CURSOR.fetchall()])
            result_list.sort()
        else:
            return {}

        # clean up the list, put it in a map
        result_map = {}
        for r in result_list:
            e = r[0:5]
            if e not in result_map:
                result_map[e] = [e + '001']
            if r not in result_map[e]:
                result_map[e].append(r)

        return result_map

    def retrieve(self, author=None, reaction=None, target=None, projectile=None, quantity=None, product=None, MF=None,
                 MT=None, C=None, S=None, I=None, SUBENT=None, ENTRY=None, pointer=None, rawEntry=False, reference=None,
                 as_JSON=False):
        """Execute a query, matching the criteria specified.
        This function returns a dictionary with the following structure:
            { ENTRY#0:[ SUBENT001, SUBENT#1, SUBENT#2, ... ], ... }.
        Here ENTRY#0 is the entry number whose subentries match the query.  The SUBENT001 is the documentation subentry
        itself, which is always included, and SUBENT#1, ... are the subentries themselves matching the search criteria.

        If the flag rawEntry is True, the raw text versions of the SUBENTs will be returned, otherwise they will be
        converted to X4Entry instances."""
        result = {}
        smap = self.query(
            author=author,
            reaction=reaction,
            target=target,
            projectile=projectile,
            quantity=quantity,
            product=product,
            MF=MF, MT=MT,
            C=C, S=S, I=I,
            SUBENT=SUBENT,
            ENTRY=ENTRY,
            pointer=pointer,
            reference=reference)

        for e in smap:
            result[e] = x4EntryFactory(e, smap[e], rawEntry=rawEntry, dataPath=self.DATAPATH)

        if as_JSON:
            import json
            import x4i.exfor_section

            class TEMPEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, x4i.exfor_section.X4DataSection):
                        return obj.as_dict()
                    return json.JSONEncoder.default(self, obj)

            return json.dumps(result, cls=TEMPEncoder)

        return result


X4DBManagerDefault = X4DBManagerPlainFS
