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
import warnings
import numpy as np
from .exfor_column_transformer import *
from .exfor_exceptions import *
from .exfor_reactions import X4ReactionCombination
from .exfor_section import X4BibMetaData
from .exfor_utilities import unique, COMMENTSTRING
from .exfor_units import *


pint_pandas.PintType.ureg = exfor_unit_registry
pint_pandas.PintType.ureg.default_format = "P~"  # by default, display units in non-silly ways
pandas.set_option('future.no_silent_downcasting', True) # this needed to supress silly pandas warning


def dataframe_from_datasection(_data):
        _columns = {}
        for _ic, _label in enumerate(_data.labels):
            _columns[_label] = pandas.Series(
                [x[_ic] for x in _data.data], 
                dtype="pint[%s]" % exfor_pint_unit_map[_data.units[_ic]])
        return pandas.DataFrame(_columns)


class X4DataSet(X4BibMetaData):

    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        """
        meta: x4i common meta data collection
        common: EXFOR COMMON section 
        reaction: REACTION instance, defaults to None 
        monitor: REACTION instance for any monitor reaction, defaults to None 
        data:  EXFOR DATA section, should be an instance of X4DataSection
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
        self.__labels = []  # what EXFOR uses for labels, and may not be what underlying dataframe will ultimately use (DO WE NEED THIS?)
        self.__units = []   # what EXFOR uses for units, we will mapt these to pint units in the pandas dataframe (DO WE NEED THIS?)
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
    
    @data.setter
    def data(self, _data):
        self.__data = _data

    @property
    def simplified(self):
        return self.__simplified

    @simplified.setter
    def simplified(self, flag):
        self.__simplified = flag
    
    def setData(self, data, common=None, pointer=None):
        """
        This should set up the data, labels and units such that all columns in all COMMON sections are in self
        and such that all columns in DATA which either have no pointer or matching pointer are in self

        inputs:
            data: DATA section, should be an instance of an X4DataSection
            common: COMMON section, should be an instance of an X4DataSection
            pointer: 3 possibilities
                - None (keep everything), 
                - ' ' (keep columns with no pointers), 
                - a number (keep columns with no pointers and the columns matching the number specified)
        """
        self.__labels = []
        self.__units = []
        self.__data = None

        # Assemble the COMMON data
        if common is not None:
            for one_common in common:
                if one_common is None: 
                    continue
                self.__labels += one_common.labels
                self.__units += one_common.units
                common_df = dataframe_from_datasection(one_common)
                try:
                    if self.__data is None:
                        self.__data = common_df
                    else:
                        self.__data = self.__data.join(common_df, how='cross')
                except ValueError as err:
                    warnings.warn(str(err) + '.  Suspect issue with COMMON fields:\n %s\n\nand\n\n %s' % (str(self.__data), str(common_df)) )
                    self.__data = common_df


        # Select out the pointer-ed columns
        temp_data = dataframe_from_datasection(data)
        drops = []
        renames = {}
        if pointer is not None:
            for col in temp_data.columns:
                if len(col) == 11 and col[-1] != ' ':  # check if column has a pointer
                    if pointer != col[-1]: # if it isn't the right one, we drop it
                        drops.append(col)
                    else: # otherwise we rename it to get rid of the pointer in the label
                        renames[col] = col[0:10].strip()
            temp_data = temp_data.drop(columns=drops)
            temp_data = temp_data.rename(columns=renames)
        
        # Final assembly
        try:
            if self.__data is None:
                self.__data = temp_data
            else:
                self.__data = self.__data.join(temp_data, how='cross')
        except ValueError as err:
            warnings.warn(str(err) + '.  Suspect issue with COMMON vs. DATA fields:\n %s\n\nand\n\n %s' % (str(self.__data), str(temp_data)) )
            self.__data = temp_data
        self.__labels += data.labels
        self.__units += data.units

        # Fix units on all special columns
        for col in self.__data:
            if "COS" in col: # cosine columns
                self.__data[col] = pandas.Series(self.__data[col].pint.magnitude, dtype="pint[cosine]")
            if "RATIO" in col: # ratio data columns
                self.__data[col] = pandas.Series(self.__data[col].pint.magnitude, dtype="pint[ratio]")

    def strHeader(self):
        out = self.xmgraceHeader()
        try:
            out += '\n' + COMMENTSTRING + '  Reaction:  ' + ' '.join(map(str, self.reaction))
        except TypeError as e:
            raise TypeError(str(e) + ', got ' + str(type(self.reaction)) + " with value " + str(self.reaction)) from e
        try:
            if self.monitor is not None:
                out += '\n' + COMMENTSTRING + '  Monitor(s): ' + ' '.join(map(str, self.monitor))
        except TypeError as e:
            raise TypeError(str(e) + ', got ' + str(type(self.monitor)) + " with value " + str(self.monitor)) from e
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

    def getSimplified(self, parserMap=None, columnNames=None, makeAllColumns=False, failIfMissingErrors=False, 
                      unitOverride=None, preferredUnits=['MeV', 'b', 'sr', 'deg', 'fm', 'b/sr']):
        """Returns a simplified version of self.
        inputs:
            parserMap:           { 'column name 1':TransformerList1, 'column name 2':TransformerList2, ... }
            columnNames:         [ 'column name 1', 'column name 2', ... ] #put them in the order *you* want
            makeAllColumns:      will make uncertainty columns even if no uncertainties are given on a particular column
            failIfMissingErrors: fail (raising exception) if missing an error column
            unitOverride:        sometimes compilers make bad choices for units, we can fix them (think mislabeled ratio data)
            preferredUnits:      list of perferred units for a problem

        What this routine does:
            - simplifies the dataframe according to the parserMap.  Typically this creates columns "X", "Y", "dX", "dY" where
              the X and Y column names are determined by the parserMap.  The parserMap is the secret sauce of this whole 
              operation.
            - when computing "dX" or "dY", the code attempts to guess the uncertainties assuming symmetric uncertainties 
              about the mean.  This means the following:
                - we make a half hearted attempt to combine all related uncertainties in quadrature 
                - we present "Min/Max" values as symmetric uncertainties about the average (Max+Min)/2, whether or not this it makes sense
                - full widths get halved
                - percent uncertainty is turned to absolute
            - converts all units in the simplified columns to rational "base" units for nuclear work, 
              e.g. MeV, b, sr, rad, fm
            - reorders columns per user request (columnNames).  This is more interesting if "makeAllColumns" is enabled, otherwise 
              you just get back the simplified data columns
        """
        results = copy.copy(self)
        
        # Check if we don't have to do anything
        if self.simplified:
            return results
        if parserMap is None:
            return results

        # Check that columnNames in sync with parserMap
        if columnNames is not None:
            for p in parserMap:
                if p not in columnNames:
                    raise KeyError(p + ' not in columnNames')

        # Override the units assumed by EXFOR's compilers
        if unitOverride is not None:
            for col, u in unitOverride.items():
                 results.data[col] = pandas.Series(results.data[col].pint.magnitude, dtype="pint[%s]" % u)

        # Convert cos(angle) => angle, sqrt(E)=>E
        for col in results.data:
            if "COS" in col:
                col_name = col.replace("COS", "ANG")
                results.data[col_name] = pandas.Series(np.arccos(results.data[col].pint.magnitude), dtype="pint[rad]")
            if hasattr(results.data[col].pint, 'units'):
                if  "squareroot_eV" in str(results.data[col].pint.units) or \
                    "squareroot_keV" in str(results.data[col].pint.units):
                    new_units = str(results.data[col].pint.units) * str(results.data[col].pint.units)
                    print(new_units)
                    results.data[col_name] = pandas.Series(np.square(results.data[col].pint.magnitude), dtype="pint[%s]" % new_units)
                    raise NotImplementedError()

        # Build new DataSeries
        _columns = {}
        for _label in parserMap:

            # load up all the parsers with the data
            for parser in parserMap[_label]:
                parser.set_data(results.data)

            # figure out which parser is the best one for the job
            best_parser, highest_parser_score = None, 0
            for parser in reversed(parserMap[_label]):
                if parser.score_label_match() >= highest_parser_score:
                    highest_parser_score = parser.score_label_match()
                    best_parser = parser

            if best_parser is not None:
                # Extract values
                values = best_parser.get_values()
                if values is None:
                    continue
                _columns[_label] = pandas.Series(values, dtype="pint[%s]" % best_parser.get_unit())
                
                # Attempt to extract uncertainties
                try:
                    uncertainties = best_parser.get_uncertainties()
                    if uncertainties is not None:
                        _columns["d(%s)" % _label] = pandas.Series(uncertainties, dtype="pint[%s]" % str(best_parser.get_unit()))
                    elif makeAllColumns:
                         _columns["d(%s)" % _label] = pandas.Series(best_parser.get_dummy_column(), dtype="pint[%s]" % str(best_parser.get_unit()))
                except pint.errors.DimensionalityError as err:
                    warnings.warn(str(err) + "indicates problem with DATA or COMMON field, check pointers?")
                except ValueError as err:
                    warnings.warn(str(err) + "indicates problem with DATA or COMMON field, check pointers?")

        # Save the data in the results
        for col in _columns:
            results.data[col] = _columns[col]

        # Convert all units to our favs
        for col in results.data.columns:
            for unit in preferredUnits:
                try:
                    results.data[col] = results.data[col].pint.to(unit)
                except:
                    pass

        # Sort the columns & make sure we have all the ones required
        if columnNames is not None:
            temp_columnNames = [c for c in columnNames if c in results.data]                        
            if failIfMissingErrors and columnNames != temp_columnNames:
                raise KeyError("No uncertainties on one or more columns")
            # How to sort columns in pandas:
            # If:      df.columns.tolist() = ['0', '1', '2', '3', 'mean']
            # Do this: df = df[['mean', '0', '1', '2', '3']]
            results.data = results.data[temp_columnNames]
        
        # All done
        results.data = results.data.fillna(0)  # final sanitization
        results.simplified = True
        return results

    def append(self, other):
        raise NotImplementedError("Do we still need this?")

    def to_csv(self, path_or_buf, index=False, dequantify=True, **kw):
        """
        Thin wrapper around pandas's to_csv()

        path_or_buf: str, path object, file-like object, or None, default None

            String, path object (implementing os.PathLike[str]), or file-like object implementing a write() function. 
            If None, the result is returned as a string. If a non-binary file object is passed, it should be opened 
            with newline='', disabling universal newlines. If a binary file object is passed, mode might need to 
            contain a 'b'.

        index: flag to control whether to display row labels
        dequantify: dequantify the pint cells before output (default=True).  If you dequantify, 
                    units appear as second row in header, otherwise they are included in each cell
        """
        if dequantify:
            return self.data.pint.dequantify().to_csv(path_or_buf, index=index, **kw)
        return self.data.to_csv(path_or_buf, index=index, **kw)

    def to_markdown(self, showindex=False, **kw):
        """Simple markedown formatted version of the dataframe, uses to_tabulate()"""
        return self.to_tabulate(showindex=showindex, headers="keys", tablefmt='markdown', units='sbs_paren', **kw) 

    def to_json(self, **kw):
        """Thin wrapper around pandas's to_json()"""
        raise NotImplementedError("Issue with PANDAS")
        return self.data.to_json(**kw)  

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
   

class X4CrossSectionDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)

    def getSimplified(self, unitOverride=None, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self, 
                                       parserMap={'Energy': incidentEnergyTransformerList, 'Data': csDataTransformerList},
                                       columnNames=['Energy', 'Data', 'd(Energy)', 'd(Data)'], 
                                       unitOverride=unitOverride,
                                       makeAllColumns=makeAllColumns,
                                       failIfMissingErrors=failIfMissingErrors)


class X4NubarDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)

    def getSimplified(self, unitOverride=None, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self, 
                                       parserMap={'Energy': incidentEnergyTransformerList, 'Data': nubarTransformerList},
                                       columnNames=['Energy', 'Data', 'd(Energy)', 'd(Data)'], 
                                       unitOverride=unitOverride,
                                       makeAllColumns=makeAllColumns,
                                       failIfMissingErrors=failIfMissingErrors)


class X4SpectrumAveCrossSectionDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)
        self.spectrum = None

    def getSimplified(self, unitOverride=None, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self, 
                                       parserMap={'Energy': spectrumArgumentTransformerList, 'Data': csDataTransformerList},
                                       columnNames=['Energy', 'Data', 'd(Energy)', 'd(Data)'], 
                                       unitOverride=unitOverride,
                                       makeAllColumns=makeAllColumns,
                                       failIfMissingErrors=failIfMissingErrors)


class X4ResonanceIntCrossSectionDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)

    def getSimplified(self, unitOverride=None, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self, 
                                       parserMap={'Data': csDataTransformerList}, columnNames=['Data'],
                                       unitOverride=unitOverride,
                                       makeAllColumns=makeAllColumns, 
                                       failIfMissingErrors=failIfMissingErrors)


class X4AnalyzingPowerDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)

    def getSimplified(self, unitOverride=None, makeAllColumns=False, failIfMissingErrors=False): return copy.copy(self)


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

    def getSimplified(self, unitOverride=None, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self, 
                                       parserMap={'Energy': incidentEnergyTransformerList, 
                                                  'Angle': angleTransformerList,
                                                  'Data': angDistTransformerList},
                                       columnNames=['Energy', 'Angle', 'Data', 'd(Energy)', 'd(Angle)', 'd(Data)'], 
                                       unitOverride=unitOverride,
                                       makeAllColumns=makeAllColumns,
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

    def getSimplified(self, unitOverride=None, makeAllColumns=False, failIfMissingErrors=False):
        return X4DataSet.getSimplified(self,
                                       parserMap={'Energy': incidentEnergyTransformerList, 
                                                  "Eout": outgoingEnergyTransformerList,
                                                  'Data': energyDistTransformerList}, 
                                       columnNames=['Energy', "Eout", 'Data', 'd(Energy)', "d(Eout)", 'd(Data)'],
                                       unitOverride=unitOverride,
                                       makeAllColumns=makeAllColumns, 
                                       failIfMissingErrors=failIfMissingErrors)


class X4EnergyAngleDistDataSet(X4DataSet):
    def __init__(self, meta=None, common=None, reaction=None, monitor=None, data=None, pointer=None):
        X4DataSet.__init__(self, meta, common, reaction, monitor, data, pointer)

    def getSimplified(self, unitOverride=None, makeAllColumns=False, failIfMissingErrors=False): raise NotImplementedError()


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
        warnings.warn("NotImplementedError: Simplification scheme for observable quantit(ies) %s not written yet" % str(','.join( quant )))
        return X4DataSet(meta, common, reaction, monitor, data, pointer)
