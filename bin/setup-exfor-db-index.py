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
#   0.     (attempt to) rework the reference handling for some corner cases (David Brown <dbrown@bnl.gov>, 2019-08-15T14:58:51)
#   1.     pickle read should have been binary (David Brown <dbrown@bnl.gov>, 2019-08-14T19:00:43)
#   2.     forgot shebang (David Brown <dbrown@bnl.gov>, 2019-08-14T17:03:46)
#   3.     can now populate reference column in theworks (Sayers, Grier Idriss (gis7617) <gis7617@lockhaven.edu>, 2019-07-26T18:50:41)
#   4.     added code to populate reference column in theworks (Sayers, Grier Idriss (gis7617) <gis7617@lockhaven.edu>, 2019-07-25T20:59:22)
#   5.     added EXFOR reference code column to theworks db (Sayers, Grier Idriss (gis7617) <gis7617@lockhaven.edu>, 2019-07-19T18:19:16)
#   6.     deal with more pickles
#          remove options that are not implemented (David Brown <dbrown@bnl.gov>, 2019-04-03T14:27:43)
#   7.     fix how we dump the pickle
#          add x4doi.txt (David Brown <dbrown@bnl.gov>, 2019-04-03T12:56:22)
#   8.     PEP-8 compliance (David Brown <dbrown@bnl.gov>, 2019-02-27T03:11:32)
#   9.     Python3.X compatibility  (David Brown <dbrown@bnl.gov>, 2018-11-16T19:46:51)
#   10.     stuff to set up test db (David Brown <dbrown@bnl.gov>, 2014-02-04T17:31:59)
#   11.     fix harmless repr() bug in chemical compounds (David Brown <dbrown@bnl.gov>, 2013-07-01T15:20:19)
#   12.     only one bug left (David Brown <dbrown@bnl.gov>, 2013-06-26T22:44:24)
#   13.     fix reference parsing
#           fix reaction parsing when have isomer projectile, isomer math at same time (David Brown <dbrown@bnl.gov>, 2013-06-26T22:32:42)
#   14.     fooled by complicated product lists no more (David Brown <dbrown@bnl.gov>, 2013-06-26T20:30:07)
#   15.     fix bug with reaction list when handling isomer math
#           add unit tests
#           lots of unit tests (David Brown <dbrown@bnl.gov>, 2013-06-26T17:51:53)
#   16.     get rid of debuggging stuff (David Brown <dbrown@bnl.gov>, 2013-06-20T15:20:52)
#   17.     fix comment (David Brown <dbrown@bnl.gov>, 2013-06-20T15:18:45)
#   18.     Deal with corner case in MONITOR format rules:
#                if a MONITOR's quantity is same as the REACTION's, you don't need to specify it in a MONITOR as
#                it should be understood (David Brown <dbrown@bnl.gov>, 2013-06-20T15:18:27)
#   19.     didn't put the module in the call to x4EntryFactory (David Brown <dbrown@bnl.gov>, 2013-06-19T14:35:49)
#   20.     use x4EntryFactory (David Brown <dbrown@bnl.gov>, 2013-06-19T13:26:04)
#   21.     switch file reads to use universal newline mode to correct bug with missing (yet important) black lines (David Brown <dbrown@bnl.gov>, 2013-06-18T21:00:59)
#   22.     rework indexing of reactions and monitors since the monitors are nontrivial generalizations of the reaction markup (David Brown <dbrown@bnl.gov>, 2013-06-18T16:53:22)
#   23.     add reaction count
#           fix bugs with monitor and coupled tallying (David Brown <dbrown@bnl.gov>, 2013-06-17T16:10:43)
#   24.     get the monitor reaction onto the monitor reaction list in a form usable by visualization widgets (David Brown <dbrown@bnl.gov>, 2013-06-15T04:08:18)
#   25.     try to make sure monitors without pointers are logged correctly (David Brown <dbrown@bnl.gov>, 2013-06-14T18:09:42)
#   26.     space out methods in classes
#           fix global data scope resolution bug (David Brown <dbrown@bnl.gov>, 2013-01-11T16:53:37)
#   27.     oops, forgot to put a bool to denote that the reaction has a monitor (David Brown <dbrown@bnl.gov>, 2013-01-10T18:42:40)
#   28.     add support for indexing monitored reactions (David Brown <dbrown@bnl.gov>, 2013-01-10T18:40:41)
#   29.     add more command line arguments for vis-coupled, simplyfy node/edge formatting (David Brown <dbrown@bnl.gov>, 2012-07-26T20:52:24)
#   30.     add doi to the database (David Brown <dbrown@bnl.gov>, 2012-07-25T14:04:23)
#   31.     add widget to put in an EXFOR master file (David Brown <dbrown@bnl.gov>, 2012-07-25T13:13:06)
#   32.     forgot about the doi file (David Brown <dbrown@bnl.gov>, 2012-07-24T15:48:33)
#   33.     planning how to split (David Brown <dbrown@bnl.gov>, 2012-07-24T15:40:55)
#   34.     fix the paths and move them into the main module __ini__.py    tell exfor_manager about them (David Brown <dbrown@bnl.gov>, 2012-07-24T15:33:16)
#   35.     unpacking works for x4c4 files (again)
#           debugged command line options (David Brown <dbrown@bnl.gov>, 2012-07-24T14:44:40)
#   36.     adding documentation, simplifying filenames (David Brown <dbrown@bnl.gov>, 2012-07-24T13:56:25)
#   37.     add the shell interpreter so htey execute OK (David Brown <dbrown@bnl.gov>, 2012-07-24T13:16:18)
#   38.     renaming the files and making them executable (David Brown <dbrown@bnl.gov>, 2012-07-24T13:14:24)
#   39.     streamline file - it should only (re)build the EXFOR index
#
################################################################################

import os
import argparse
import collections
from x4i import DATAPATH, fullIndexFileName, fullErrorFileName, fullCoupledFileName, fullMonitoredFileName, \
    fullReactionCountFileName, fullDBPath, fullDoiFileName, exfor_file_glob

# ------------------------------------------------------
# Global data
# ------------------------------------------------------

buggyEntries = {}
coupledReactionEntries = {}
monitoredReactionEntries = {}
reactionCount = {}


# ------------------------------------------------------
#   Tools to actually build the database
# ------------------------------------------------------
def buildDOIIndex(doiFile, verbose=False): # creates doiXref database
    """
    Adds the DOI cross reference table to the main index.
    The IAEA should probably tightly associated this data with the EXFOR data, but for some reason it is not.
    """
    import sqlite3

    # set up database & create the table
    connection = sqlite3.connect(fullIndexFileName)
    cursor = connection.cursor()
    cursor.execute("""drop table if exists doiXref""")
    cursor.execute("""create table doiXref (entry text, nsr text, doi text, reference text )""")

    for line in open(doiFile).readlines():
        entry = line[32:46].strip().replace('$ENTRY=', '')
        nsr = line[46:61].strip().replace('$NSR=', '')
        doi = line[61:].strip().replace('$DOI=', '')
        reference = line[0:32].strip().replace('$REF=', '')
        cursor.execute("insert into doiXref values(?,?,?,?)", (entry, nsr, doi, reference))

    # commit & close connection to database
    connection.commit()
    cursor.close()


def buildMainIndex(verbose=False, stopOnException=False):
    """
    This function build up the index of the database.

    The database is assumed to be in the ``x4i/data/db`` directory (set by the
    ``dbPath`` global variable).  The directory is arranged as follows ::

        db/001/00011.x4
               00012.x4
               ...
           002/00021.x4
               ...
          ...

    You can probable guess the columns in our sqlite3 database since we use this
    index to support the follow searches ::

        AUTHOR:
            author = None

        REACTION:
            reaction = None
            target = None
            projectile = None
            quantity = None
            product = None
            MF = None
            MT = None
            C = None
            S = None
            I = None

        SUBENT = None

        ENTRY = None

    """
    import sqlite3
    import pickle
    import pprint
    import glob
    import pyparsing
    import multiprocessing
    from x4i import exfor_exceptions

    # clean up previous runs
    if os.path.exists(fullIndexFileName):
        os.remove(fullIndexFileName)
    if os.path.exists(fullErrorFileName):
        os.remove(fullErrorFileName)
    if os.path.exists(fullCoupledFileName):
        os.remove(fullCoupledFileName)
    if os.path.exists(fullReactionCountFileName):
        os.remove(fullReactionCountFileName)
    if os.path.exists(fullMonitoredFileName):
        os.remove(fullMonitoredFileName)

    # set up database & create the table
    connection = sqlite3.connect(fullIndexFileName)
    cursor = connection.cursor()
    cursor.execute(
        "create table if not exists theworks (entry text, subent text, pointer text, author text, reaction text, "
        "projectile text, target text, quantity text, rxncombo bool, monitored bool, reference text)")

    # Guts of the entry processing
    def process_entry_guts(_f, _cursor, _coupledReactionEntries, _monitoredReactionEntries, _reactionCount, 
                           _buggyEntries, _DEBUG=False, _verbose=False, _stopOnException=False):
        if _DEBUG:  # Then we are debugging
            skipme = True
            # "12763.20363.22188.22782.41434.41541.A0026.A0206.A0208.A0222.A0227.A0291.A0425.A0462.A0578.A0648.
            # A0650.A0727.A0882.A0926.C0082.C0256.C0299.C0346.C1248.C1654.D0046.D6011.D6043.D6170.E1306.E1792.E2324.
            # E2371.G0016.G4035.M0763.M0806",  '20363.22188.22782.41434.41541'

            for myENTRYForTesting in '11125.30230'.split('.'):
                if myENTRYForTesting in _f:
                    skipme = False
            if skipme:
                return False

        if _verbose:
            print('    ', _f)

        try:
            processEntry(_f,
                         _cursor,
                         _coupledReactionEntries,
                         _monitoredReactionEntries,
                         _reactionCount,
                         verbose=_verbose)
        except (
                exfor_exceptions.IsomerMathParsingError,
                exfor_exceptions.ReferenceParsingError,
                exfor_exceptions.ParticleParsingError,
                exfor_exceptions.AuthorParsingError,
                exfor_exceptions.InstituteParsingError,
                exfor_exceptions.ReactionParsingError,
                exfor_exceptions.BrokenNumberError) as err:
            _buggyEntries[f] = (err, str(err))
            return not _stopOnException  # if we are supposed to stop, then _stopOnException will be True and this run failed
        except (Exception, pyparsing.ParseException) as err:
            _buggyEntries[f] = (err, str(err))
            return not _stopOnException  # if we are supposed to stop, then _stopOnException will be True and this run failed
        
        return True  # presummed success
        


    # build up the table
    try:
        if verbose:
            print(exfor_file_glob(DATAPATH)) 

        for f in glob.glob(exfor_file_glob(DATAPATH)):  
            if not \
                process_entry_guts(f, cursor, coupledReactionEntries, monitoredReactionEntries, reactionCount, 
                                   buggyEntries, _DEBUG=False, _verbose=verbose, _stopOnException=stopOnException):
                break
 
    except KeyboardInterrupt:
        pass
    except Exception as err:
        print("Encountered error:", repr(err), str(err))
        print("Saving work")

    # log all the errors
    if verbose:
        print('\nNumber of Buggy Entries:', len(buggyEntries))
        print('\nBuggy entries:')
        pprint.pprint(buggyEntries)
    pickle.dump(buggyEntries, open(fullErrorFileName, mode='wb'))

    # log all the coupled data sets
    if verbose:
        print('\nNumber of entries with coupled data sets:', len(coupledReactionEntries))
        print('\nNumber of entries with reaction monitors sets:', len(monitoredReactionEntries))
        print('\nNumber of distinct reactions:', len(reactionCount))
    pickle.dump(coupledReactionEntries, open(fullCoupledFileName, mode='wb'))
    pickle.dump(monitoredReactionEntries, open(fullMonitoredFileName, mode='wb'))
    pickle.dump(reactionCount, open(fullReactionCountFileName, mode='wb'))

    # commit & close connection to database
    connection.commit()
    cursor.close()


def getQuantity(quantList):
    """
    Most quantities are the 1st ones in the quantity list
    ... but there are a lot of important exceptions ...
    ... 'POT' is the exceptions to the exceptions ...
    """
    for q in ['AA', 'AKE/DA', 'AKE', 'AMP', 'AP', 'AP/DA', 'COR', 'COR/DE', 'CRL', 'DA/RAT', 'DA', 'DA/DE', 'DA/DP',
              'DA/CRL', 'DA/DA', 'DA/DA/DE', 'DA/DE', 'DA/KE', 'DA/TMP', 'DE', 'FM/DA', 'FY', 'FY/DE', 'FY/RAT',
              'FY/SUM', 'FY/CRL', 'INT', 'INT/DA', 'ISP', 'KE', 'KE/CRL', 'MCO', 'MLT', 'NU', 'NU/DE', 'POL',
              'POL/DA/DE', 'POL/DA', 'POL/DA/DA/DE', 'RI', 'SPC', 'SPC/DMT/DR', 'SPC/DPT/DR', 'SPC/DR', 'PY', 'SIG',
              'SIG/RAT', 'SIG/SUM', 'TTY', 'TTY/DA/DE', 'TTY/DA', 'WID', 'WID/RED', 'WID/STR', 'ZP']:
        if q in quantList:
            return q
    if 'POT' in quantList:
        return 'POT'
    return quantList[0]


SimpleReaction = collections.namedtuple("SimpleReaction", "proj targ prod rtext quant simpleRxn")


def getSimpleReaction(complicatedReaction):
    proj = repr(complicatedReaction.proj)
    targ = '-'.join(repr(complicatedReaction.targ).split('-')[1:])
    prod = '+'.join(map(repr, complicatedReaction.products)).replace("'", "")
    resid = repr(complicatedReaction.residual)
    rtext = (proj + "," + prod).upper()
    quant = getQuantity(complicatedReaction.quantity)
    if '-M' in resid:
        simpleRxn = (targ + '(' + rtext + ')' + resid, quant)
    else:
        simpleRxn = (targ + '(' + rtext + ')', quant)
    return SimpleReaction(proj, targ, prod, rtext, quant, simpleRxn)


def extract_reference_code(line):
    """
    Loops through the reference codes and comments and returns the
    reference code contained with the outermost set of parenthesis
    """
    count = -1
    last = 0

    for character in line:
        if character == '(':
            if type(count) != type(int):
                count = 0
            count += 1
        elif character == ')':
            count -= 1
        if count == 0:
            break
        last += 1

    return line[line.find('(')+1:last]


def processEntry(entryFileName, cursor=None, coupledReactionEntries={}, monitoredReactionEntries={}, reactionCount={},
                 verbose=False):
    """
    Computes the rows for a single entry and puts it in the database
    """
    from x4i import exfor_entry, exfor_reactions, exfor_manager
    if verbose:
        print('        ', entryFileName.split(os.sep)[-1], end=' ')
    e = exfor_entry.x4EntryFactory(entryFileName.split(os.sep)[-1].split('.')[0], filePath=entryFileName)
    doc_bib = e[1]['BIB']
    try:
        m = e.meta().legend()
        print(str(e.accnum) + ':', m)
    except Exception as err:
        print(err)
    auth = []  # author field
    inst = []  # institute field
    refcodes = None # reference field
    if 'AUTHOR' in doc_bib:
        auth = doc_bib['AUTHOR'].author_family_names
    if 'INSTITUTE' in doc_bib:
        inst = doc_bib['INSTITUTE']
    if 'REFERENCE' in doc_bib:
        refcodes = doc_bib['REFERENCE']

    if verbose:
        print('        ', "Num. authors:", len(auth))
        print('        ', "Num. institutes:", len(inst))
        print()

    for snum in e.sortedKeys()[1:]:
        rxnf = {}  # reaction field
        monf = None  # monitor field
        if 'BIB' in e[snum]:
            bib = e[snum]['BIB']
            if 'REACTION' in bib:
                rxnf = bib['REACTION']
            if 'MONITOR' in bib:
                monf = bib['MONITOR']
        if auth == [] and 'AUTHOR' in doc_bib:
            auth = doc_bib['AUTHOR'].author_family_names
        if inst == [] and 'INSTITUTE' in doc_bib:
            inst = doc_bib['INSTITUTE']
        if rxnf == {} and 'REACTION' in doc_bib:
            rxnf = doc_bib['REACTION']
        if monf is None and 'MONITOR' in doc_bib:
            monf = doc_bib['MONITOR']
        if refcodes == {} or refcodes is None:
            try:
                refcodes = e[snum]['BIB']['REFERENCE']
            except KeyError:
                refcodes = { '': "()" }

        nrxns = 0
        nmons = 0
        if cursor is not None:
            for p in rxnf:
                if verbose:
                    if p == ' ':
                        print('            ' + str(e.accnum) + ', SUBENT: ' + str(snum))
                    else:
                        print('            ' + str(e.accnum) + ', SUBENT: ' + str(snum) + ', pointer:', p)

                    # Get the reactions as a list
                meas = rxnf.reactions[p][0]
                if isinstance(meas, exfor_reactions.X4ReactionCombination):
                    rxns = meas.getReactionList()
                elif isinstance(meas, exfor_reactions.X4ReactionIsomerCombination):
                    rxns = meas.getReactionList()
                elif isinstance(meas, exfor_reactions.X4Reaction):
                    rxns = [meas]
                else:
                    raise TypeError('got type ' + str(type(meas)))
                rxn_combo = len(rxns) > 1
                nrxns += len(rxns)

                # Get the monitors as a list
                monitored_rxn = (monf is not None and p in monf)
                if monitored_rxn:
                    mons = []
                    for rMon in monf.reactions[p]:
                        measMon = rMon[0]
                        if isinstance(measMon, exfor_reactions.X4ReactionCombination):
                            mons += measMon.getReactionList()
                        elif isinstance(measMon, exfor_reactions.X4ReactionIsomerCombination):
                            mons += measMon.getReactionList()
                        elif isinstance(measMon, exfor_reactions.X4Reaction):
                            mons += [measMon]
                        elif measMon is None:
                            pass
                        else:
                            raise TypeError('got type ' + str(type(measMon)))
                    nmons += len(mons)

                if rxn_combo:
                    coupledReactionEntries[(e.accnum, snum, p)] = []
                if monitored_rxn:
                    monitoredReactionEntries[(e.accnum, snum, p)] = []

                # Put the monitors in the monitor pickle and the reaction count pickle
                if monitored_rxn:
                    for mon in mons:

                        # Deal with corner case in MONITOR format rules:
                        #   if a MONITOR's quantity is same as the REACTION's, you don't need to specify it in a
                        #   MONITOR as it should be understood
                        if not mon.quantity:
                            mon.quantity = rxnf.reactions[p][0].quantity

                        simpleRxnMon = getSimpleReaction(mon)
                        monitoredReactionEntries[(e.accnum, snum, p)].append(simpleRxnMon.simpleRxn)
                        if simpleRxnMon.simpleRxn not in reactionCount:
                            reactionCount[simpleRxnMon.simpleRxn] = 0
                        reactionCount[simpleRxnMon.simpleRxn] += 1

                        if verbose:
                            print('               ', simpleRxnMon.simpleRxn, '(Monitor)')

                # Put the reactions in the coupled pickle, the reaction count pickle and the index itself
                for r in rxns:
                    simpleRxn = getSimpleReaction(r)
                    if verbose:
                        if rxn_combo:
                            print('               ', simpleRxn.simpleRxn, '(Combo)')
                        else:
                            print('               ', simpleRxn.simpleRxn)

                    for reference_pointer, references in refcodes.items():
                        for reference_code in references:
                            clean_reference = extract_reference_code(reference_code) # clean_reference is reference free from parenthesis & comments

                            for a in auth: # this is the "population loop"
                                #                        print "insert into theworks values(?,?,?,?,?,?,?,?,?) ", \
                                #                            ( e.accnum, snum, p, a, simpleRxn.rtext, simpleRxn.proj,
                                #                            repr(simpleRxn.targ), simpleRxn.quant, rxn_combo, monitored_rxn )    +-------------------+
                                cursor.execute("insert into theworks values(?,?,?,?,?,?,?,?,?,?,?)",#                             |  this populates   |
                                               (e.accnum, snum, p, a, simpleRxn.rtext, simpleRxn.proj, simpleRxn.targ,#           |  the database     |
                                                simpleRxn.quant, rxn_combo, monitored_rxn, clean_reference))#                     +-------------------+

                    if simpleRxn.simpleRxn not in reactionCount:
                        reactionCount[simpleRxn.simpleRxn] = 0
                    reactionCount[simpleRxn.simpleRxn] += 1

                    if rxn_combo:
                        coupledReactionEntries[(e.accnum, snum, p)].append(simpleRxn.simpleRxn)
                    if monitored_rxn:
                        monitoredReactionEntries[(e.accnum, snum, p)].append(simpleRxn.simpleRxn)

        if verbose:
            print('           ', "Num. reactions:", nrxns)
            print('           ', "Num. monitors:", nmons)
            print()


# ------------------------------------------------------
#   Error reporting
# ------------------------------------------------------

def reportErrors(outFile, verbose=False):
    import pickle
    import csv

    with open(fullErrorFileName, mode='rb') as pickleFile:
        f = pickle.load(pickleFile)
        sortedErrors = {}
        for i in f:
            t = type(f[i][0])
            if t not in sortedErrors:
                sortedErrors[t] = []
            sortedErrors[t].append(i)

    # Full report to a csv file
    with open(outFile, mode='w') as csvFile:
        fullReport = csv.writer(csvFile)
        fullReport.writerow(["Error", "Number Occurances", "Entry", "Full Message"])
        for i in sortedErrors:
            for j in range(len(sortedErrors[i])):
                example = f[sortedErrors[i][j]][1]
                entry = sortedErrors[i][j].replace('.x4', '')
                if j == 0:
                    row = [repr(i), str(len(sortedErrors[i])), entry, example]
                else:
                    row = [" ", " ", entry, example]
                fullReport.writerow(row)


def viewErrors(verbose=False):
    import pickle

    with open(fullErrorFileName, mode='rb') as pickleFile:
        f = pickle.load(pickleFile)
        sortedErrors = {}
        for i in f:
            t = type(f[i][0])
            if t not in sortedErrors:
                sortedErrors[t] = []
            sortedErrors[t].append(i)

    # Quick Report to stdout:
    print("Error".rjust(55), " ", "Num.", " ", "Example".ljust(74), " ", "Entry")
    for i in sortedErrors:
        for j in range(len(sortedErrors[i])):
            example = f[sortedErrors[i][j]][1]
            if len(example) > 70:
                example = example[0:70] + '...'
            example = example.ljust(74)
            entry = sortedErrors[i][j].replace('.x4', '')
            if j == 0:
                print(repr(i).rjust(55), " ", str(len(sortedErrors[i])).ljust(4), " ", example, " ", entry)
            else:
                print(55 * " ", " ", 4 * " ", " ", example, " ", entry)


# ------------------------------------------------------
#  Main !!
# ------------------------------------------------------
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Manage the installation & update of x4i's internal copy of the EXFOR database.")
    if True:
        parser.set_defaults(verbose=False)
        parser.add_argument("-v", action="store_true", dest='verbose', help="Enable verbose output")
        parser.add_argument("-q", action="store_false", dest='verbose', help="Disable verbose output")

        # ------- Control over update actions -------
        parser.add_argument("--build-index", dest='build_index', action="store_true", default=True,
                            help="Just (re)builds the sqlite database indexing the EXFOR data in the project.  "
                                 "The EXFOR data must be already installed.")
        parser.add_argument("--no-build-index", dest='build_index', action="store_false", 
                            help="Do not (re)builds the sqlite database indexing the EXFOR data in the project.")

        # ------- View/save logs -------
        parser.add_argument("--view-errors", action="store_true", default=False,
                            help="View all errors encountered while building the database index.")
        parser.add_argument('--error-log', metavar="CSVFILE", type=str, default=None,
                            help="Write all the errors encountered when generating the index of the EXFOR files to "
                                 "this file.  This is a csv formatted file suitable for viewing in MS Excel.")
        parser.add_argument('--coupled-log', metavar="CSVFILE", type=str, default=None,
                            help="Write all the coupled data encountered when generating the index of the EXFOR files "
                                 "to this file.  This is a csv formatted file suitable for viewing in MS Excel.")

        # ------- Misc -------
        parser.add_argument("--doi", type=str, default=None,
                            help='Reinstall the EXFOR doi <-> entry mapping using the contents from this IAEA EXFOR '
                                 'dictionary text file.')

    args = parser.parse_args()

    if args.build_index:
        buildMainIndex(verbose=args.verbose)
        buildDOIIndex(fullDoiFileName, verbose=args.verbose)

    # ------- View/save logs -------
    if args.error_log is not None:
        reportErrors(args.error_log, verbose=args.verbose)
    if args.coupled_log is not None:
        raise NotImplementedError()
    if args.view_errors:
        viewErrors(verbose=args.verbose)
