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
#   0.     Get rid of extra line feed in CSV output (David Brown <dbrown@bnl.gov>, 2021-09-20T15:27:17)
#   1.     Add len() function (David Brown <dbrown@bnl.gov>, 2021-09-13T15:37:58)
#   2.     Add two more variations on plain old cross sections (David Brown <dbrown@bnl.gov>, 2019-02-27T03:11:16)
#   3.     Rework append() algorithm to throw exceptions instead of simply whining (David Brown <dbrown@bnl.gov>, 2018-12-06T16:34:27)
#   4.     Rework __str__ function of an X4DataSet so that can handle slight differences in treatment of str() on floats between py3 & py4    fix bug in table fuzzy-diff    use new fuzzy-diff everywhere (David Brown <dbrown@bnl.gov>, 2018-12-06T15:47:57)
#   5.     Undo attempts to update universal newline support flags (David Brown <dbrown@bnl.gov>, 2018-12-05T17:09:40)
#   6.     Update CSV file management for Python3.X (David Brown <dbrown@bnl.gov>, 2018-12-05T02:01:43)
#   7.     Python3.X porting issue: {}.keys() returns view, not list (David Brown <dbrown@bnl.gov>, 2018-12-04T22:02:30)
#   8.     Python3.X compatibility & PEP-8 compliance (David Brown <dbrown@bnl.gov>, 2018-12-04T21:48:44)
#   9.     Uncommitted tweaks to paper;
#          An exfor data set now can parse RI correctly
#          GND particle names as option (David Brown <dbrown@bnl.gov>, 2016-06-29T18:34:25)
#   10.    Fix initialization bug revealed by unit test (David Brown <dbrown@bnl.gov>, 2014-09-08T13:41:22)
#   11.    Flatten inheritance hierarchy, it was needlessly deep (David Brown <dbrown@bnl.gov>, 2014-03-04T21:40:56)
#   12.    Add flags to catch coupled data and to catch unsimplified data (David Brown <dbrown@bnl.gov>, 2014-03-04T17:30:10)
#   13.    Tweaks to column parsing to attempt to workaround momentum and temperature data
#          (The whole column parsing architecture needs to be redone, probably with PQU's help) (David Brown <dbrown@bnl.gov>, 2014-03-04T16:44:43)
#   14.    Get rid of an unused variable;
#          Fix typo: raise non-existant exception (David Brown <dbrown@bnl.gov>, 2014-03-04T13:35:59)
#   15.    Fix str() bug when making fancy headers w/o Monitors (David Brown <dbrown@bnl.gov>, 2013-10-10T15:12:56)
#   16.    Add sort() function so that if entries retrieve in a different order, the test won't fail (David Brown <dbrown@bnl.gov>, 2013-10-10T14:24:09)
#   17.    Fix another missing monitor wiring bug (David Brown <dbrown@bnl.gov>, 2013-06-19T14:26:39)
#   18.    Streamline X4Entry initialization, hopefully also squashing bugs along the way (David Brown <dbrown@bnl.gov>, 2013-06-19T12:02:54)
#   19.    Switch file reads to use universal newline mode to correct bug with missing (yet important) black lines (David Brown <dbrown@bnl.gov>, 2013-06-18T21:00:59)
#   20.    Parsing even really complicated monitors now work and all are printed when you print a data set (David Brown <dbrown@bnl.gov>, 2013-06-18T14:40:59)
#   21.    Add monitor as option to DataSets and the DataSetFactory (David Brown <dbrown@bnl.gov>, 2013-06-18T12:38:08)
#   22.    Regenerate index, make coupled pickle;
#          Make so datasets can still be printed out even if they cannot be fully parsed (David Brown <dbrown@bnl.gov>, 2012-01-05T14:56:01)
#   23.    Attempting to do isomer math (David Brown <dbrown@bnl.gov>, 2012-01-04T21:10:25)
#
################################################################################
from __future__ import print_function, division

import copy
import pint 
import pint_pandas
import pandas
import tabulate
from .exfor_column_parsing import *
from .exfor_exceptions import *
from .exfor_reactions import X4ReactionCombination
from .exfor_section import X4BibMetaData
from .exfor_utilities import unique, COMMENTSTRING
from .exfor_units import *


pint_pandas.PintType.ureg.default_format = "P~"  # by default, display units in non-silly ways


def dataframe_from_datasection(_data):
        _columns = {}
        for _ic, _label in enumerate(_data.labels):
            _columns[_label] = pandas.Series(
                [x[_ic] for x in _data.data], 
                dtype="pint[%s]" % exfor_pint_unit_map[_data.units[_ic]])
        return pandas.DataFrame(_columns)


class X4DataSetNew(X4BibMetaData):

    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        """
        meta: x4i common meta data collection
        common: EXFOR COMMON section 
        reaction: REACTION instance, defaults to None 
        monitor: REACTION instance for any monitor reaction, defaults to None 
        data:  EXFOR DATA section
        pointer: ugh, the EXFOR pointer for the dataset, defaults to None
        """
        # Initialize merged meta data, a needlessly complicated process
        X4BibMetaData.__init__(self, author="None", institute="None", title="None", pubType="None", year="None")
        if meta is not None:
            for m in meta:
                if m is None:
                    continue
                for k in m.__slots__:
                    if not getattr(m, k) in [None, "None"]:
                        setattr(self, k, getattr(m, k))

        # Intialize important operational flags
        self.__simplified = False
        self.__pointer = pointer  # To deal with EXFOR's strange pointer implementation

        # Initializing the reaction is easy!
        self.__reaction = reaction
        self.__monitor = monitor
        if reaction is None:
            self.__coupled = False
        else:
            self.__coupled = isinstance(reaction[0], X4ReactionCombination)

        # Initializing the data is less so...
        self.__labels = []  # what EXFOR uses for labels, and may not be what underlying dataframe will ultimately use
        self.__units = []   # what EXFOR uses for units, we will mapt these to pint units in the pandas dataframe
        self.__data = None  # this will be a pint-powered pandas dataframe
        self.__simplified = False
        if data is not None:
            self.setData(data, common, pointer)

    @property
    def reaction(self):
        return self.__reaction

    @property
    def monitor(self):
        return self.__monitor
    
    @property
    def coupled(self):
        return self.__coupled
    
    @property
    def pointer(self):
        return self.__pointer

    @property
    def labels(self):
        return self.__labels

    @property
    def units(self):
        return self.__units
    
    @property
    def data(self):
        return self.__data
    
    @property
    def simplified(self):
        return self.__simplified
    
    def setData(self, data, common=None, pointer=None):
        """
        This should set up the data, labels and units such that all columns in all COMMON sections are in self
        and such that all columns in DATA which either have no pointer or matching pointer are in self
        """
        if pointer is not None:
            raise NotImplementedError("add pointers")
        if common is not None:
            self.__labels = common.labels + data.labels
            self.__units = common.units + data.units
            common_df = dataframe_from_datasection(common)
            data_df = dataframe_from_datasection(data)
            raise NotImplementedError("adding common")
        else:
            self.__data = dataframe_from_datasection(data)
            self.__labels = data.labels
            self.__units = data.units

    def strHeader(self):
        out = self.xmgraceHeader()
        try:
            out += '\n' + COMMENTSTRING + '  Reaction:  ' + ' '.join(map(str, self.reaction))
        except TypeError as e:
            raise TypeError(str(e) + ', got ' + str(type(self.reaction)) + " with value " + str(self.reaction))
        try:
            if self.monitor is not None:
                out += '\n' + COMMENTSTRING + '  Monitor(s): ' + ' '.join(map(str, self.monitor))
        except TypeError as e:
            raise TypeError(str(e) + ', got ' + str(type(self.monitor)) + " with value " + str(self.monitor))
        return out

    def reprHeader(self):
        result = X4BibMetaData.__repr__(self) + ' \nReaction:  ' + repr(self.reaction[0])
        if self.monitor is not None and len(self.monitor) > 0:
            result += ' \nMonitor(s):' + repr([x[0] for x in self.monitor])
        result += "\n"
        return result

    def __str__(self):
        body = self.to_tabulate(tablefmt='plain', units='stacked')
        splbody = body.split('\n')
        return '\n'.join(
            [
                self.strHeader(),
                '#        ' + splbody[0],
                '#        ' + splbody[1],
            ] + ['         '+x for x in splbody[2:]])

    def __repr__(self):
        return self.reprHeader() + self.to_tabulate(tablefmt='plain', units='stacked')

    def __len__(self):
        return len(self.data)

    def sort(self, **kw):
        """In place sort, see Python documentation for list().sort()"""
        raise NotImplementedError("Do we still need this?")

    def getSimplified(self, parserMap=None, columnNames=None, makeAllColumns=False, failIfMissingErrors=False):
        """Returns a simplified version of self.
        inputs:
            parserMap            = { 'column name 1':parserList1, 'column name 2':parserList2, ... }
            columnNames          = [ 'column name 1', 'column name 2', ... ] #put them in the order *you* want
            makeAllColumns       will make uncertainty columns even if no uncertainties are given on a particular column
            failIfMissingErrors  fail (raising exception) if missing an error column
        """        
        raise NotImplementedError()

    def append(self, other):
        raise NotImplementedError("Do we still need this?")

    def to_csv(self, f, **kw):
        """Thin wrapper around pandas's to_csv()"""
        self.data.to_csv(f, **kw)

    def to_markdown(self, showindex=False, **kw):
        """Simple markedown formatted version of the dataframe, uses to_tabulate()"""
        self.to_tabulate(self, showindex=showindex, headers="keys", tablefmt='markdown', units='sbs_paren', **kw) 

    def to_json(self, **kw):
        """Thin wrapper around pandas's to_json()"""
        self.data.to_json(**kw)  

    def to_tabulate(self, showindex=False, headers="keys", tablefmt='psql', units=None, **kw):
        """
        showindex: controls whether to show the pandas index column(s), passed through to tabulate
        headers: controls header display, passed through to tabulate if units are None, otherwise
                 we try to maintain tabulate rules, namely: 
                - "keys": will generate from column keys, but adding units per units keyword
                - "firstrow": will generate from first row of data, but adding units per units keyword (basically same as "keys")
                - list of strings: use the given strings as labels, but adding units per units keyword
        tablefmt: controls table format, passed through to tabulate.  Some table formats do not like stacked units
                  (markdown for instance), we leave that to the user to experiment what works best
        units: None - do not show units row in header
               "sbs" - show units side-by-side with column label
               "stacked" - show units vertically stacked under the column label
               "sbs_paren" - show units side-by-side with column label, but in parenthesis
               "stacked_paren" - show units vertically stacked under the column label, but in parenthesis
        **kw: any other keywords tabulate might like are just passed though
        """
        column_labels = self.data.columns.tolist()
        if units is None:
            headers = column_labels
        else:
            if type(headers) in [tuple, list]: 
                column_labels = headers # going to save the user-specified headers & rebuild the list                
            if "_paren" in units:
                column_units = ["("+str(x.units)+")" for x in self.data.dtypes.tolist()] 
            else:
                column_units = [str(x.units) for x in self.data.dtypes.tolist()]
            headers = []
            if "stacked" in units:
                for i in range(len(column_labels)):
                    headers.append(column_labels[i]+'\n'+column_units[i])
            else:
                for i in range(len(column_labels)):
                    headers.append(column_labels[i]+' '+column_units[i])
        return tabulate.tabulate(self.data.pint.dequantify(), showindex=showindex, headers=headers, tablefmt=tablefmt, **kw)

    def numcols(self):
        return self.data.shape[1]

    def numrows(self):
        return self.data.shape[0]

    def __getitem__(self, k):
        if not isinstance(k,tuple) or len(k)!=2:
            raise TypeError("key must be a tuple of length 2")
        return self.data[k[0]][k[1]]
   

class X4DataSet(X4BibMetaData):

    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        # Initialize merged meta data, a needlessly complicated process
        X4BibMetaData.__init__(self, author="None", institute="None", title="None", pubType="None", year="None")
        if meta is not None:
            for m in meta:
                if m is None:
                    continue
                for k in m.__slots__:
                    if not getattr(m, k) in [None, "None"]:
                        setattr(self, k, getattr(m, k))
        # Initializing the reaction is easy!
        self.reaction = reaction
        self.monitor = monitor
        # Initializing the data is less so...
        self.labels = []
        self.units = []
        self.data = []
        self.simplified = False
        if reaction is None:
            self.coupled = False
        else:
            self.coupled = isinstance(reaction[0], X4ReactionCombination)
        if data is not None:
            self.setData(data, common, pointer)

    def setData(self, data, common=None, pointer=None):
        """This should set up the data, labels and units such that all columns in all COMMON sections are in self
        and such that all columns in DATA which either have no pointer or matching pointer are in self"""
        # Set up the column labels & units (filter on pointers here...)
        column_offsets = []  # where current dataset's columns begin
        column_filter = []
        if common is None:
            full_data = [data]
        else:
            full_data = common + [data]
        for d in full_data:
            column_offsets.append(len(self.labels))
            if d is None:
                continue
            other_pointers_columns = []
            for p in filter(lambda x: x != pointer, d.pointers.keys()): other_pointers_columns += d.pointers[p]
            for icol in range(d.numcols):
                if d.pointers == {} or icol not in other_pointers_columns:
                    column_filter.append(True)
                    self.labels.append(d.labels[icol][0:10].strip())
                    self.units.append(d.units[icol][0:10].strip())
                else:
                    column_filter.append(False)
        # add the data itself
        for irow in range(data.numrows):
            row = column_offsets[2] * [0]
            icol = len(row)
            for x in data.data[irow]:
                if column_filter[icol]:
                    row.append(x)
                icol += 1
            self.data.append(row)
        # now add the common data, there'd better not be pointers here!
        if common is not None:
            for c in common:
                if c is None:
                    continue
                if c.numrows == 1:  # copy the rows to all rows in data
                    for irow in range(data.numrows):
                        for icol in range(c.numcols):
                            self.data[irow][column_offsets[common.index(c)] + icol] = c[0, icol]
                else:  # copy to the first numrows
                    for irow in range(min(c.numrows, data.numrows)):
                        for icol in range(c.numcols):
                            self.data[irow][column_offsets[common.index(c)] + icol] = c[irow, icol]

    def strHeader(self):
        out = self.xmgraceHeader()
        try:
            out += '\n' + COMMENTSTRING + '  Reaction:  ' + ' '.join(map(str, self.reaction))
        except TypeError as e:
            raise TypeError(str(e) + ', got ' + str(type(self.reaction)) + " with value " + str(self.reaction))
        try:
            if self.monitor is not None:
                out += '\n' + COMMENTSTRING + '  Monitor(s): ' + ' '.join(map(str, self.monitor))
        except TypeError as e:
            raise TypeError(str(e) + ', got ' + str(type(self.monitor)) + " with value " + str(self.monitor))
        return out

    def reprHeader(self):
        result = X4BibMetaData.__repr__(self) + ' \nReaction:  ' + repr(self.reaction[0])
        if self.monitor is not None and len(self.monitor) > 0:
            result += ' \nMonitor(s):' + repr([x[0] for x in self.monitor])
        result += "\n"
        return result

    def __str__(self):
        return '\n'.join(
            [
                self.strHeader(),
                '#        ' + ' '.join([str(i).ljust(13) for i in self.labels]) + ' ',
                '#        ' + ' '.join([str(i).ljust(13) for i in self.units]) + ' '] +
            ['        ' + ' '.join([str(j).ljust(13) for j in i]) + ' ' for i in self.data])

    def __repr__(self):
        ans = self.reprHeader() + "["
        ans += "['" + "','".join(self.labels) + "']" + ",\n"
        ans += "['" + "','".join(self.units) + "']"
        for row in self.data:
            ans += ",\n" + "[" + ",".join(map(str, row)) + "]"
        ans += "]"
        return ans

    def __len__(self):
        return len(self.data)

    def sort(self, **kw):
        """In place sort, see Python documentation for list().sort()"""
        self.data.sort(**kw)

    def getSimplified(self, parserMap=None, columnNames=None, makeAllColumns=False, failIfMissingErrors=False):
        """Returns a simplified version of self.
        inputs:
            parserMap            = { 'column name 1':parserList1, 'column name 2':parserList2, ... }
            columnNames          = [ 'column name 1', 'column name 2', ... ] #put them in the order *you* want
            makeAllColumns       will make uncertainty columns even if no uncertainties are given on a particular column
            failIfMissingErrors  fail (raising exception) if missing an error column
        """
        result = copy.copy(self)
        if self.simplified:
            return result
        numrows = result.numrows()
        if parserMap is None:
            return result
        # Check that columnNames in sync with parserMap
        if columnNames is not None:
            for p in parserMap:
                if p not in columnNames:
                    raise KeyError(p + ' not in columnNames')
        # Initialize things
        vals = {}
        errs = {}
        no_errs = {}
        result.data = []
        result.labels = []
        result.units = []
        if columnNames is None:
            return result
        # initialize val, err values
        for parser in parserMap:
            vals[parser] = reduce(condenseColumn, [i.getValue(self) for i in parserMap[parser]])
            errs[parser] = reduce(condenseColumn, [i.getError(self) for i in parserMap[parser]])
            no_errs[parser] = errs[parser][2:] == [None for i in errs[parser][2:]]
            if vals[parser][2:] == [None for i in vals[parser][2:]]:
                raise NoValuesGivenError(parser)
        # Put the data into the result
        # Make the column headings & units, first
        for column in columnNames:
            result.labels.append(column)
            result.units.append(vals[column][1])
        # Now the column labels & units for the uncertainties
        for column in columnNames:
            if not no_errs[column] or makeAllColumns:
                result.labels.append('d(' + column + ')')
                if no_errs[column]:
                    result.units.append(vals[column][1])
                else:
                    result.units.append(errs[column][1])
        # Now assemble the rows & add them to result.data
        for i in range(2, numrows + 2):
            row = []
            for col in columnNames:
                row.append(vals[col][i])
            for col in columnNames:
                if no_errs[col]:
                    if makeAllColumns:
                        row.append(0.0)
                    elif failIfMissingErrors:
                        raise NoUncertaintyGivenError(col)
                else:
                    row.append(errs[col][i])
            result.data.append(row)
        result.simplified = True
        return result

    def append(self, other):
        if self.labels == [] and self.units == [] and self.data == []:
            self.reaction = copy.copy(other.reaction)
            self.monitor = copy.copy(other.monitor)
            self.labels = copy.copy(other.labels)
            self.units = copy.copy(other.units)
            self.data = copy.copy(other.data)
            self.simplified = copy.copy(other.simplified)
            return
        if self.labels == other.labels and self.units == other.units and str(self.reaction[0]) == str(
                other.reaction[0]):
            for row in other.data:
                self.data.append(copy.copy(row))
        else:
            why = []
            if self.labels != other.labels:
                why.append("Labels don't match: " + str(self.labels) + ' vs. ' + str(other.labels))
            if self.units != other.units:
                why.append("Units don't match: " + str(self.units) + ' vs. ' + str(other.units))
            if self.reaction != other.reaction:
                why.append("Reactions don't match: " + str(self.reaction[0]) + " vs. " + str(other.reaction[0]))
            if self.monitor != other.monitor:
                why.append("Monitors don't match: " + str(self.monitor) + " vs. " + str(other.monitor))
            raise TypeError("Can't add datasets because " + ' and '.join(why))
        return

    def csv(self, f):
        import csv
        with open(f, mode="w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows([self.labels, self.units] + self.data)

    def numcols(self):
        return len(self.labels)

    def numrows(self):
        return len(self.data)

    def __getitem__(self, k):
        if not isinstance(k,tuple) or len(k)!=2:
            raise TypeError("key must be a tuple of length 2")
        i,j=k
        if type(i) == str:
            if i == 'LABELS':
                return self.labels[j]
            elif i == 'UNITS':
                return self.units[j]
            else:
                raise KeyError('Invalid index: ' + i)
        else:
            return self.data[i][j]


class X4CrossSectionDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)

    def getSimplified(self, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self, parserMap={'Energy': incidentEnergyParserList, 'Data': csDataParserList},
                                       columnNames=['Energy', 'Data'], makeAllColumns=makeAllColumns,
                                       failIfMissingErrors=failIfMissingErrors)


class X4NubarDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)

    def getSimplified(self, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self, parserMap={'Energy': incidentEnergyParserList, 'Data': nubarParserList},
                                       columnNames=['Energy', 'Data'], makeAllColumns=makeAllColumns,
                                       failIfMissingErrors=failIfMissingErrors)


class X4SpectrumAveCrossSectionDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)
        self.spectrum = None

    def getSimplified(self, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self, parserMap={'Energy': spectrumArgumentParserList, 'Data': csDataParserList},
                                       columnNames=['Energy', 'Data'], makeAllColumns=makeAllColumns,
                                       failIfMissingErrors=failIfMissingErrors)


class X4ResonanceIntCrossSectionDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)

    def getSimplified(self, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self, parserMap={'Data': csDataParserList}, columnNames=['Data'],
                                       makeAllColumns=makeAllColumns, failIfMissingErrors=failIfMissingErrors)


class X4AnalyzingPowerDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)

    def getSimplified(self, makeAllColumns=False, failIfMissingErrors=False): return copy.copy(self)


class X4AngularDistributionDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)
        self.referenceFrame = 'Lab'
        for col in self.labels:
            if '-CM' in col:
                self.referenceFrame = "Center of mass"
                break

    def strHeader(self):
        out = X4DataSet.strHeader(self)
        out += '\n' + COMMENTSTRING + '  Frame:     ' + self.referenceFrame
        return out

    def getSimplified(self, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self, parserMap={'Energy': incidentEnergyParserList, 'Angle': angleParserList,
                                                        'Data': angDistParserList},
                                       columnNames=['Energy', 'Angle', 'Data'], makeAllColumns=makeAllColumns,
                                       failIfMissingErrors=failIfMissingErrors)


class X4EnergyDistributionDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)
        self.referenceFrame = 'Lab'
        for col in self.labels:
            if '-CM' in col:
                self.referenceFrame = "Center of mass"
                break

    def strHeader(self):
        out = X4DataSet.strHeader(self)
        out += '\n' + COMMENTSTRING + '  Frame:     ' + self.referenceFrame
        return out

    def getSimplified(self, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self,
                                       parserMap={'Energy': incidentEnergyParserList, "E'": outgoingEnergyParserList,
                                                  'Data': energyDistParserList}, columnNames=['Energy', "E'", 'Data'],
                                       makeAllColumns=makeAllColumns, failIfMissingErrors=failIfMissingErrors)


class X4EnergyAngleDistDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)

    def getSimplified(self, makeAllColumns=False, failIfMissingErrors=False): raise NotImplementedError()


def X4DataSetFactory(quant, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
    if quant == 'Coupled':
        quant_list = unique([i.quantity for i in reaction[0].reaction_list])
        if len(quant_list) == 1:
            quant = quant_list[0]
        else:
            raise NotImplementedError("Coupled data with different quantities in expression:" + str(reaction[0]))
    if quant == ['SIG']:
        return X4CrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['CN', 'SIG']:
        return X4CrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'DERIV']:
        return X4CrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'FCT']:
        return X4CrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'TTA']:
        return X4CrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'RAW']:
        return X4CrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['DI', 'SIG']:
        return X4CrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'EVAL']:
        return X4CrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'EXP']:
        return X4CrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'MXW']:
        return X4SpectrumAveCrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'SPA']:
        return X4SpectrumAveCrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'SFC', 'EVAL']:
        return X4SpectrumAveCrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'SFC', 'EXP']:
        return X4SpectrumAveCrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'SFC']:
        return X4SpectrumAveCrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'FST']:
        return X4SpectrumAveCrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'RTE']:
        return X4SpectrumAveCrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'FIS']:
        return X4SpectrumAveCrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'FIS', 'EVAL']:
        return X4SpectrumAveCrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif quant == ['SIG', 'AV']:
        return X4CrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif 'RI' in quant:
        return X4ResonanceIntCrossSectionDataSet(meta, common, reaction, monitor, data, pointer)
    elif 'POL/DA' in quant:
        return X4AnalyzingPowerDataSet(meta, common, reaction, monitor, data, pointer)
    elif 'DA' in quant:
        return X4AngularDistributionDataSet(meta, common, reaction, monitor, data, pointer)
    elif 'NU' in quant:
        return X4NubarDataSet(meta, common, reaction, monitor, data, pointer)
    elif 'DE' in quant:
        return X4EnergyDistributionDataSet(meta, common, reaction, monitor, data, pointer)
    else:
        # raise NotImplementedError( "Unknown observable quantity: " + ','.join( quant ) )
        return X4DataSet(meta, common, reaction, monitor, data, pointer)
