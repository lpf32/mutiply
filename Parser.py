#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
from collections import OrderedDict


class RecursionOverLimit(Exception):

    def __str__(self):
        return "Second section recursive"


class ExtendInIParser(object):

    def __init__(self):
        self._sections = OrderedDict()
        self._default = OrderedDict()
        self._extra = OrderedDict()
        self._top = OrderedDict()
        self._second = OrderedDict()
        self._filename = None

    def _verify_line(self, line):
        index = 0
        j = 0
        for i in line:
            if i == '[':
                index += 1
                j = index
            if i == ']':
                j -= 1

        if j != 0:
            return -1
        else:
            return index

    def _get_section_content(self, line, level):
        return line[level:len(line)-level]

    def _read(self, fd):
        '''
        level
            0   内容
            1   top
            2   second
        '''
        lineno = 0
        while True:
            line = fd.readline()
            lineno += 1
            if not line:
                break
            if line.strip() == '':
                continue
            level = self._verify_line(line.strip())
            if level == -1:
                raise ConfigParser.MissingSectionHeaderError(self._filename, lineno, line)
            if level == 1:
                self._sections.update({self._get_section_content(line.strip(), level): []})
            if level == 0:
                last_key = next(reversed(self._sections))
                self._sections[last_key].append(line.strip())
            if level == 2:
                last_key = next(reversed(self._sections))
                self._sections[last_key].append(line.strip())

    def _process_section(self, sections):
        self._remove_second_section(sections)
        self._get_target_dict()

    def _get_target_dict(self):
        for key in self._sections.keys():
            temp = OrderedDict()
            for i in self._sections.get(key):
                temp.update({i.split('=')[0]: i.split('=')[1]})
            self._sections[key] = temp

    def options(self, section):
        try:
            _section = self._sections[section]
        except KeyError:
            raise ConfigParser.NoSectionError(section)
        return [key for key in _section]

    def get(self, section, option):
        try:
            _section = self._sections[section]
        except KeyError:
            raise ConfigParser.NoSectionError(section)

        try:
            _option = _section[option]
        except KeyError:
            raise ConfigParser.NoOptionError(option, section)

        return _option

    def _remove_second_section(self, sections):
        sections = sorted(sections, key=lambda x: [e.startswith('[') for e in x[1]])
        if self._flter(sections[0][1], self._has_section):
            raise RecursionOverLimit()
        else:
            temp = []
            head = sections[0]
            second_mode = self._get_second_mode(head[0])
            for i in sections[1:]:

                if second_mode in i[1]:
                    index = i[1].index(second_mode)
                    k = 0
                    for j in head[1]:
                        k += 1
                        i[1].insert(index+k, j)
                    i[1].pop(index)

            for i in sections:
                temp.extend(i[1])
            if not self._flter(temp, self._has_section):
                return sections
            else:
                self._remove_second_section(sections[1:])

    def _get_second_mode(self, string):
        return "[[" + string + "]]"

    def _has_section(self, line):
        return line.startswith('[')

    def _flter(self, object, callback):
        temp = []
        for i in object:
            if callback(i):
                temp.append(i)
        return temp

    def read(self, filename):
        if isinstance(filename, basestring):
            self._filename = filename
            with open(filename, "r+") as fd:
                self._read(fd)
                self._process_section(self._sections.items())