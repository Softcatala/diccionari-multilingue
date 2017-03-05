#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import urllib
import json
import yaml

class CheckContentQuality(object):

    def __init__(self, url):
        self.url = url

    def _get_results(self, url):
        urllib.urlretrieve(url, 'file.txt')
        with open('file.txt') as json_data:
            data = json.load(json_data)
            return data

    def _assert_that(self, actual, expected, word):
        if not expected == actual:
            text = u"Expected '{0}' equals '{1}' for '{2}'"
            text = text.format(expected, actual, word).encode('utf-8')
            raise Exception(text)

    def _assert_greater(self, actual, minimum):
        if minimum > actual:
            text = u'Expected {0} to be greater than minimum {1}'
            raise Exception(text.format(minimum, actual))

    def _check_words(self):

        with open('quality-words.yaml', 'r') as f:
            doc = yaml.load(f)
            for entry in doc:
                word = unicode(entry['word_ca'])
                definition = entry['definition_ca']
                url = u'{0}search/{1}?it=1'
                url = url.format(self.url, word).encode('utf-8')
                json = self._get_results(url)
                found = False
                for rslt in json:
                    if 'word_ca' not in rslt or 'definition_ca' not in rslt:
                        continue

                    if rslt['word_ca'] == word and rslt['definition_ca'] == definition:
                        found = True
                        break

                self._assert_that(found, True, word)

    # Checks that all index entries return some words and the total count
    def _check_index_content(self):
        total_words = 0
        for c in map(chr, range(ord('a'), ord('z')+1)):
            c = '{0}'.format(c)
            url = '{0}index/' + c
            url = url.format(self.url)
            json = self._get_results(url)
            words = len(json['words'])
            total_words += words
            if c != 'y':
                self._assert_greater(words, 1)

        self._assert_greater(total_words, 8500)

    def _check_all_sources_uploaded(self):
        
        url = '{0}statistics'
        url = url.format(self.url)
        json = self._get_results(url)
        self._assert_that('wikidata' in json, True, 'wikidata')
        self._assert_that('wikidictionary' in json, True, 'wikidictionary')

    def check(self):
        self._check_words()
        self._check_all_sources_uploaded()
        self._check_index_content()
        return True
