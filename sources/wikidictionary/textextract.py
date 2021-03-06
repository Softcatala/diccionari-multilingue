#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2015 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import logging
import StringIO
import re

class TextExtract:

    def __init__(self, text):
        self.text = text

    '''Wiki internal link with format [[LINK|TEXT]]'''
    def _remove_intenal_links(self, line):
        SECTION_START = '[['
        SECTION_END = ']]'

        start = line.find(SECTION_START)
        if start < 0:
            return line

        end = line.find(SECTION_END, start)
        if end < 0:
            return line

        '''[[CONTENT]]'''
        original = line[start:end + len(SECTION_END)]

        LINK_SEPARATOR = '|'
        start_lsp = line.find(LINK_SEPARATOR, start)
        if start_lsp < 0:
            text = line[start + len(SECTION_START) : end]
        else:
            text = line[start_lsp + len(LINK_SEPARATOR) : end]            

        final = line[:start] + text + line[end + len(SECTION_END) :len(line)]
        logging.debug("Removed link '{0}' -> '{1}'".format(line.encode('utf-8'), 
            final.encode('utf-8')))

        return self._remove_intenal_links(final)

    def _remove_mediawiki_markup(self, line):
        MEDIAWIKI_BOLD = "'''"
        MEDIAWIKI_ITALIC = "''"

        final = line.replace(MEDIAWIKI_BOLD, '')
        final = final.replace(MEDIAWIKI_ITALIC, '')
        return final

    def _remove_templates(self, line):
        SECTION_START = '{{'
        SECTION_END = '}}'

        start = line.find(SECTION_START)
        if start < 0:
            return line

        end = line.find(SECTION_END, start + len(SECTION_START))
        if end < 0:
            return line

        end += len(SECTION_END)
        final = line[:start] + line[end:len(line)]
        return self._remove_templates(final)

    # <ref name="diec"></ref><ref name="grec"></ref><ref name="dcvb"></ref>
    def _remove_xml_tags(self, line):
        return re.sub('<[^>]*>', '', line)  

    def GetDescription(self):
        verb = ''
        VERB_START = '===[ ]*Verb[ ]*==='
        ADV_START = '===[ ]*Adverbi[ ]*==='
        ADJ_START = '===[ ]*Adjectiu[ ]*==='
       
        found = True
        match = re.search(VERB_START, self.text)
        if match is None:
            found = False

        if found is True:
            start = match.end()
            end = self.text.find('==', start)
            if end < 0:
                found = False

        if found is False:
            found = True
            match = re.search(ADV_START, self.text)
            if match is None:
                found = False

            if found is True:
                start = match.end()
                end = self.text.find('==', start)
                if end < 0:
                    found = False

        if found is False:
            found = True
            match = re.search(ADJ_START, self.text)
            if match is None:
                found = False

            if found is True:
                start = match.end()
                end = self.text.find('==', start)
                if end < 0:
                    found = False

        if found is False:
            return verb

        s = self.text[start:end]
        buf = StringIO.StringIO(s)

        while True:
            s = buf.readline()
            if len(s) == 0:
                break

            # If we find a {{-sin-}}, {{-trad-}}, etc, stop processing
            if '{{-' in s.lower():
                break

            s = self._remove_templates(s)
            s = self._remove_intenal_links(s)
            s = self._remove_mediawiki_markup(s)
            s = self._remove_xml_tags(s)

            if re.search('[a-zA-Z]', s) is None:
                logging.debug("Discard:" + s)
                continue

            if s.isspace():
                logging.debug("Discard:" + s)
                continue

            verb += s

        return verb
