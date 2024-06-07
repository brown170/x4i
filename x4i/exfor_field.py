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
#   0.     improved author parsing
#          improved reaction parsing error reporting (David Brown <dbrown@bnl.gov>, 2019-08-16T17:26:18)
#   1.     make sure output is sorted by pointer in ALL cases
#          adjust unit test accordingly (David Brown <dbrown@bnl.gov>, 2018-12-05T20:03:27)
#   2.     dealing with map() and open() issues (David Brown <dbrown@bnl.gov>, 2018-12-05T19:49:24)
#   3.     get rid of more bad-behaving map() functions (David Brown <dbrown@bnl.gov>, 2018-12-05T17:55:16)
#   4.     grammar is spelled "grammar" not "grammer" (David Brown <dbrown@bnl.gov>, 2018-12-05T16:41:09)
#   5.     pyparsing import fix (David Brown <dbrown@bnl.gov>, 2018-12-04T22:15:06)
#   6.     py3 porting issue: {}.keys() returns view, not list (David Brown <dbrown@bnl.gov>, 2018-12-04T22:02:30)
#   7.     fixing imports (David Brown <dbrown@bnl.gov>, 2018-12-04T21:09:44)
#   8.     Python3.X compatibility & PEP-8 compliance (David Brown <dbrown@bnl.gov>, 2018-12-04T17:44:23)
#   9.     fix reference parsing
#          fix reaction parsing when have isomer projectile, isomer math at same time (David Brown <dbrown@bnl.gov>, 2013-06-26T22:32:42)
#   10.    fix bug with reaction list when handling isomer math
#          add unit tests
#          lots of unit tests (David Brown <dbrown@bnl.gov>, 2013-06-26T17:51:53)
#   11.     handle pathological author list (David Brown <dbrown@bnl.gov>, 2013-06-26T15:40:35)
#   12.     rip out debugging stuff (David Brown <dbrown@bnl.gov>, 2013-06-20T15:14:44)
#   13.     fix field parsing in presence of blank lines that maybe have to be preserved (David Brown <dbrown@bnl.gov>, 2013-06-19T19:28:24)
#   14.     parsing even really complicated monitors now work and all are printed when you print a data set (David Brown <dbrown@bnl.gov>, 2013-06-18T14:40:59)
#   15.     trying to get monitors working (David Brown <dbrown@bnl.gov>, 2013-06-18T13:26:10)
#   16.     start work debugging monitor field (David Brown <dbrown@bnl.gov>, 2013-06-18T12:01:04)
#   17.     correct parsing of monitors to properly distinguish between multiple monitors and those with associated column headings in DATA section (David Brown <dbrown@bnl.gov>, 2013-01-11T18:58:32)
#   18.     monitors now parsed and packed into a data structure (David Brown <dbrown@bnl.gov>, 2013-01-10T15:55:39)
#   19.     add X4MonitorField & add blank line between member functions for clarity (David Brown <dbrown@bnl.gov>, 2013-01-08T19:31:15)
#   20.     add a reaction list function that we can use to substitute in the getEquation() function (David Brown <dbrown@bnl.gov>, 2012-09-11T12:37:21)
#   21.     make getEquantion() return schematic or actual reactions (David Brown <dbrown@bnl.gov>, 2012-09-11T02:53:59)
#   22.     getEquation() when the equation actually is easy to get (David Brown <dbrown@bnl.gov>, 2012-09-11T02:46:53)
#   23.     add widget to extract the reaction equation (esp. useful for coupled reactions)
#           use widget to collect improved statistics on the coupled data -- in preparation for making the COMMARA cross material covariance (David Brown <dbrown@bnl.gov>, 2012-08-01T03:17:24)
#   24.     fix author list parsing when there are no authors given (David Brown <dbrown@bnl.gov>, 2012-01-03T16:49:22)
#
################################################################################

from __future__ import print_function, division

import x4i.exfor_reactions as exfor_reactions
import x4i.exfor_dicts as exfor_dicts
import x4i.exfor_grammars as exfor_grammars
import x4i.exfor_reference as exfor_reference
import x4i.exfor_exceptions as exfor_exceptions
import pyparsing
import copy


def chunkifyX4TextField(oldtext):
    """
    Splits an EXFOR text field into chunks, code pieces ( i.e. "(blah, blah)" ) get there own chunks and "free text"
    get their own chunks.  Works best on 'INSTITUTE' field.  Would be better to move to pyparsing based scheme.
    @type  oldtext: string
    @param oldtext: raw line from an EXFOR file
    @rtype: list of strings
    @return: list containing the (hopefully) parsed Exfor text field
    """
    if type(oldtext) != str:
        raise TypeError
    text = exfor_grammars.x4textfield.parseString(oldtext)
    return text.asList()


def extractX4FieldType(field):
    """
    Extracts the type of field from an EXFOR field.  It should be in cols[0:10] of the field string.
    @type  field: string
    @param field: string containing the EXFOR field
    @rtype: string or None
    @return: the name of the field
    """
    tag = field[0][0:10].strip()
    if tag == '':
        return None
    return tag


def extractX4FieldPointer(field):
    """
    Extracts a pointer (if it exists) from an EXFOR field.  It should be in column 10 of the field string.
    @type  field: string
    @param field: string containing the EXFOR field
    @rtype: string or None
    @return: the pointer or None if there is none
    """
    tag = field[0][10:11].strip()
    if tag == '':
        return None
    return tag


class X4SubField(list):
    """
    smallest element of an EXFOR text field; may span several lines
    """

    def __str__(self):
        """Pretty version of subfield (if one exists)"""
        return ' '.join([x.strip() for x in self])

    def __repr__(self):
        """EXFOR formatting back"""
        return '\n'.join([11 * ' ' + x for x in self])


class X4PlainField(dict):
    """
    EXFOR plain data field in a Bib Section, with extra character grabbed from tag field to catch possible pointers
    """

    def __init__(self, raw_field=None):
        dict.__init__(self)
        self.tag = raw_field[0][0:10].strip()
        pointer = ' '
        if raw_field is not None:
            for line in raw_field:
                line = line.ljust(66)  # fill lines to 66 characters
                if line[10] != ' ':
                    pointer = line[10]
                if pointer not in self:
                    self[pointer] = X4SubField()
                self[pointer].append(line[11:66].rstrip())
        self.sorted_keys = list(self.keys())
        self.sorted_keys.sort()

    def total_len(self):
        return sum([len(self[p]) for p in self])

    def __str__(self):
        """Pretty version of field (if one exists)"""
        result = []
        for p in self.sorted_keys:
            if p != ' ':
                result.append('[' + p + '] ' + str(self[p]))
            else:
                result.append(str(self[p]))
        return '; '.join(result)

    def __repr__(self):
        """Gets you back the EXFOR field"""
        result = []
        for p in self.sorted_keys:
            s = repr(self[p])
            result.append(s[:10] + p + s[11:])
        return self.tag.ljust(10) + ('\n'.join(result))[10:]


class X4ReactionField(X4PlainField):
    """Parsed EXFOR Reaction Field"""

    def __init__(self, x):
        X4PlainField.__init__(self, x)  # this should chop reaction field into separate measurements, 1/pointer
        self.reactions = {}
        for p in self:
            d = str(self[p])
            try:
                f = exfor_reactions.x4reactionfield.parseString(d)
            except pyparsing.ParseException as err:
                raise exfor_exceptions.ReactionParsingError(
                    'Can not parse reaction "' + d + '",\n    got error "' + str(err) + '"\n   ')
            self.reactions[p] = [self.getMeasurementType(f[0:-1]), f[-1]]

    def getMeasurementType(self, x):
        try:
            for i in ['(', ')', '+', '-', '*', '/', '=', '//']:
                if i in x:
                    return exfor_reactions.X4ReactionCombination(x)
            return exfor_reactions.X4Reaction(x[0])
        except exfor_exceptions.IsomerMathParsingError:
            return exfor_reactions.X4ReactionIsomerCombination(x)

    def getEquation(self, key, schematic=False):
        """
        Produced a list of strings corresponding to the parsed reaction field.

        Arguments ::

            * key : the EXFOR pointer (either '' or an integer)
            * schematic : If True, will return the equation with the strings "rxn 0", 'rxn 1' etc.
                where the reactions used to be.  This is good for computer algebra.  If False,
                the repr() of the X4Reaction instance.
        """
        result = []
        i = 0
        if isinstance(self.reactions[key][0], exfor_reactions.X4Reaction):
            if schematic:
                return 'rxn 0'
            else:
                return repr(self.reactions[key][0])
        for thing in self.reactions[key][0].data:
            if not isinstance(thing, str):
                if schematic:
                    result.append('rxn ' + str(i))
                else:
                    result.append(repr(thing))
                i += 1
            else:
                result.append(thing)
        return result

    def getX4ReactionList(self, key):
        """
        Produce a list of X4Reaction instances that are present in a reaction string.  For a
        simple reaction, this is a one element list with the X4Reaction instance in it.  For a
        reaction combination, this is a list of X4Reaction instances, entered in order of
        occurrence in the reaction string.  The list can be used to fill in the schematic output from
        getEquation() to produce the non-schematic version.

        Arguments:

            * key : the EXFOR pointer (either '' or an integer)
        """
        if isinstance(self.reactions[key][0], exfor_reactions.X4Reaction):
            return [self.reactions[key][0]]
        result = []
        for thing in self.reactions[key][0].data:
            if isinstance(thing, exfor_reactions.X4Reaction):
                result.append(thing)
        return result

    def __str__(self):
        ans = []
        if self.reactions == {}:
            return ans
        for j in self.sorted_keys:
            if j == ' ':
                ans.append(str(self.reactions[j][0]))
            else:
                ans.append('[' + j + '] ' + str(self.reactions[j][0]))
                if self.reactions[j][1] != '':
                    ans[-1] += ', ' + self.reactions[j][1]
        return '; '.join(ans)


class X4MonitorField(X4ReactionField):
    """
    Parsed Exfor Monitor Field

    The reaction monitors are stored in the ``reactions`` data member, just like an regular X4ReactionField.
    This is a Python dict who's keys are a reaction pointer (' ' if there isn't one) and
    value are a list of all monitors for this reaction.  The elements of the list of
    monitors are a 3-tuple: ( X4Reaction, free text, DATA column reference ) ::

        - The X4Reaction, is the monitor reaction
        - The free text is free text entered by the EXFOR compiler
        - The DATA column reference is the column header of the monitor reaction data
          given in the DATA section of this EXFOR subentry.
    """

    def __init__(self, x):
        X4PlainField.__init__(self, x)  # this should chop reaction field into separate measurements, 1/pointer

        self.reactions = {}

        for p in self:
            self.reactions[p] = []

            # Chop field into reactions
            ds = []

            lineQueue = copy.copy(self[p])
            while lineQueue:
                line = lineQueue.pop(0)

                # Case 1: ((MONIT#(REACTION)) style formatting -- may extend on several lines
                if line.strip().startswith('(('):
                    ds.append(line)
                    if ds[-1].count('(') != ds[-1].count(')'):
                        ds[-1] += lineQueue.pop(0)

                # Case 2: (REACTION) style formatting -- may also extend on several lines
                elif line.strip().startswith('('):
                    ds.append(line)
                    if ds[-1].count('(') != ds[-1].count(')'):
                        ds += lineQueue.pop(0)

                # Case 3: Free Text -- may also extend on several lines, let the continuation logic catch this
                elif len(ds) == 0:
                    ds.append(line.strip())

                # A regular continuation line
                else:
                    ds[-1] += ' ' + line.strip()

            # Process each reaction
            for d in ds:
                heading = None
                if 'MONIT' in d:
                    for s in d.split('((MONIT')[1:]:
                        i = s.index(')')
                        d = '(' + s[i + 1:]
                        heading = "MONIT" + s[:i]
                if d.startswith('('):
                    try:
                        f = exfor_reactions.x4reactionfield.parseString(d)
                        self.reactions[p].append((self.getMeasurementType(f[0:-1]), f[-1], heading))
                    except pyparsing.ParseException as err:
                        raise exfor_exceptions.ReactionParsingError(
                            'Can not parse reaction "%s" (part of "%s"),\n    got error %s\n   '% (d, str(ds), str(err)))
                else:
                    self.reactions[p].append((None, d, heading))

    def __str__(self):
        ans = []
        if self.reactions == {}: return ans
        for j in self.sorted_keys:
            if j == ' ':
                ans.append(str(self.reactions[j]))
            else:
                ans.append('[' + j + '] ' + str(self.reactions[j]))
        return '; '.join(ans)


pubTypeMap = {'A': 'Abstract', 'K': 'Abstract of Journal', 'J': 'Journal', 'C': 'Conf. Proc.', 'S': 'Conf. Proc.',
              'P': 'Prog. Report', 'R': 'Lab Report', 'B': 'Book', 'W': 'Private Comm.', 'T': 'Thesis', 'X': 'Preprint'}


class X4ReferenceField(X4PlainField):
    """Parsed EXFOR reference field"""

    def __init__(self, x):
        X4PlainField.__init__(self, x)
        self.refs = {}
        try:
            for p in self:
                refs = []
                self.refs[p] = []
                intautology = False
                hastautology = False
                for line in self[p]:
                    if line[0:2] == '((':
                        intautology = True
                        hastautology = True
                        refs.append(line.replace('\n', ''))
                    elif not intautology and line[0:1] == '(':
                        refs.append(line.replace('\n', ''))
                    else:
                        refs[-1] += line.replace('\n', '')
                    if '))' in line:
                        intautology = False
                for xx in refs:
                    if hastautology and '=' in xx:
                        try:
                            xref = exfor_reference.x4refcodetautology.parseString(xx).asList()
                        except pyparsing.ParseException as err:
                            raise exfor_exceptions.ReferenceParsingError(
                                'Can not parse reference "' + xx + '",\n    got error "' + str(err) + '"\n   ')
                        refcomment = xref[-1]
                        for xxx in xref[0:-1]:
                            try:
                                if xxx != '=':
                                    self.refs[p].append(
                                        (exfor_reference.X4ReferenceCode(self.flatten(xxx)), refcomment))
                            except (KeyError, pyparsing.ParseException, LookupError, AssertionError) as err:
                                raise exfor_exceptions.ReferenceParsingError(
                                    'Can not parse reference "' + xx + '",\n    got error "' + str(err) + '"\n   ')
                    else:
                        xref = exfor_reference.x4refcode.parseString(xx).asList()
                        refcomment = xref[-1]
                        try:
                            self.refs[p].append((exfor_reference.X4ReferenceCode(self.flatten(xref[0])), refcomment))
                        except (KeyError, pyparsing.ParseException, LookupError, AssertionError) as err:
                            raise exfor_exceptions.ReferenceParsingError(
                                'Can not parse reference "' + xx + '",\n    got error "' + str(err) + '"\n   ')
            # Take this reference main info from first reference in field that we could parse
            for p in self.refs:
                if isinstance(self.refs[p][0][0], exfor_reference.X4ReferenceCode):
                    self.reftype = self.refs[p][0][0].reftype
                    self.name = self.refs[p][0][0].name
                    self.details = self.refs[p][0][0].details
                    self.date = self.refs[p][0][0].date
                    self.pubyear = self.refs[p][0][0].pubyear
                    self.pubtype = pubTypeMap[self.reftype]
                    break
        except exfor_exceptions.ReferenceParsingError:
            self.reftype = '?'
            self.name = 'Parsing failed'
            self.details = '?'
            self.date = '?'
            self.pubyear = '?'
            self.pubtype = '?'

    def flatten(self, l):
        """flattens nested parens in volume part of a reference"""
        if len(l) == 1:
            return l[0]

        def parens(x):
            if type(x) == list:
                return '(' + x[0] + ')'
            return x

        return ''.join([parens(xx) for xx in l])

    def __str__(self):
        """Pretty version of field"""
        l = []
        for p in self.refs:
            if p == ' ':
                l.append('')
            else:
                l.append('[' + p + ']')
            l[-1] += '; '.join([str(x[0]) for x in self.refs[p]])
        return '; '.join(l)


class X4TitleField(X4PlainField):
    """Cleaned up title"""

    def __init__(self, x):
        X4PlainField.__init__(self, x)

    def __str__(self):
        '''Pretty version of field'''
        result = []
        for p in self.sorted_keys:
            result.append(str(self[p]).title().strip())
        return ' '.join(result)


class X4AuthorField(X4PlainField):
    """Cleaned up author list"""

    def __init__(self, x):
        self.authors = []
        self.extraData = ''
        for noAuthorString in ["No author given", ".NOT GIVEN.", "Not given"]:
            if noAuthorString in '\n'.join(x):
                self.author_family_names = []
                return
        X4PlainField.__init__(self, x)
        for p in self:
            t = ''.join([x.strip() for x in self[p]])
            try:
                tt = exfor_grammars.x4refcode.parseString(t).asList()
            except pyparsing.ParseException as err:
                try:
                    tt = exfor_grammars.x4refcode.parseString(t.split(')')[0] + ')').asList()
                except Exception:
                    raise exfor_exceptions.AuthorParsingError(
                        'Can not parse authors "' + x + '",\n    got error "' + str(
                            err) + '" when parsing as x4refcode\n   ')
            try:
                ttt = exfor_grammars.x4authorlist.parseString(' '.join(tt[0])).asList()
            except pyparsing.ParseException as err:
                raise exfor_exceptions.AuthorParsingError('Can not parse authors "' + x + '",\n    got error "' + str(
                    err) + '" when parsing as x4authorlist\n   ')
            self.authors += [x.title() for x in ttt]
        self.author_family_names = [x.split('.')[-1] for x in self.authors]

    def __str__(self):
        """Pretty version of field"""
        if self.authors == []:
            return "No author given"
        return ', '.join(self.authors)


class X4InstituteField(X4PlainField):
    """Cleaned up institutes list"""

    def __init__(self, x):
        X4PlainField.__init__(self, x)
        self.institutes = []
        for p in self:
            try:
                pil = exfor_grammars.x4institutefield.parseString(str(self[p])).asList()
            except pyparsing.ParseException as err:
                raise exfor_exceptions.InstituteParsingError(
                    'Can not parse institute "' + str(x) + '",\n    got error "' + str(err) + '"\n   ')
            il = {}
            ikey = None
            for tok in pil:
                if type(tok)==list:  # is an institute
                    for ikey in tok:
                        il[ikey] = []
                else:   # is part of a comment on the last institute entry
                    il[ikey].append(tok.title())
            for ikey in il:          
                comment_string = ' '.join(il[ikey])
                try:
                    self.institutes.append((ikey, exfor_dicts.get_exfor_dict_entry('Institutes', ikey)['expansion'], comment_string))
                except:
                    self.institutes.append((ikey, ikey, comment_string))

    def __str__(self):
        """Pretty version of field"""
        inst = []
        for i in self.institutes:
            entry = i[1]
            if i[2] != '': entry += ' (' + i[2] + ')'
            inst.append(entry)
        return '; '.join(inst)
