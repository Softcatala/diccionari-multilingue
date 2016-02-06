#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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

import urllib
import json

class CheckApi(object):

    def __init__(self, url):
        self.url = url

    def _get_results(self, url):
        urllib.urlretrieve(url, 'file.txt')
        with open('file.txt') as json_data:
            data = json.load(json_data)
            return data

    def _assert_contains(self, actual, expected):
        if expected not in actual:
            text = u"Expected '{0}' contains '{1}"
            raise Exception(text.format(expected, actual))

    def _assert_that(self, actual, expected):
        if not expected == actual:
            text = u"Expected '{0}' equals '{1}'"
            raise Exception(text.format(expected, actual))

    def _check_autocomplete(self):
        url = '{0}api/autocomplete/tau'
        url = url.format(self.url)
        json = self._get_results(url)

        words = json['words']
        self._assert_contains(words, 'taula')
        self._assert_contains(words, 'taulell')

    def _check_index(self):
        url = '{0}api/index/a'
        url = url.format(self.url)
        json = self._get_results(url)

        words = json['words']
        self._assert_contains(words, u'abadia')
        self._assert_contains(words, u'avís')

    def _check_search(self):
        url = '{0}api/search/abat'
        url = url.format(self.url)
        json = self._get_results(url)
        self._assert_concret_word(json[0])

    def _check_search_langs(self):
        langs = {"en" : "abbot", "fr" : "abbé", "es" : "abad", "it" : "abate", "de" : "Abt"}

        for lang in langs.keys():
            word = langs[lang]
            url = '{0}api/search/{1}?lang={2}&it=1'
            url = url.format(self.url, word, lang)
            json = self._get_results(url)
            self._assert_concret_word(json[0])

    def _assert_concret_word(self, term):
        self._assert_that(term['word_ca'], 'abat')
        self._assert_that(term["definition_es"], u"título dado al superior de una abadía o monasterio")
        self._assert_that(term["references"]["wikiquote_ca"], "Abat")
        self._assert_that(term["image"], "Abbatia%20CIST%20Sbernadiensis%2027a.jpg")
        self._assert_that(term["definition_fr"], u"titre religieux donné à celui qui dirige une abbaye")
        self._assert_that(term["references"]["gec"], "0073593")
        self._assert_that(term["definition_de"], "Vorsteher einer Abtei und kirchliches Amt")
        self._assert_that(term["definition_en"], "religious title")
        self._assert_that(term["word_en"], "abbot")
        self._assert_that(term["word_fr"], u"abbé")
        self._assert_that(term["word_de"], "Abt")
        self._assert_that(term["references"]["wikidata"], "Q103163")
        self._assert_that(term["word_es"], "abad")
        self._assert_that(term["word_ca"], "abat")

    def check(self):

        self._check_autocomplete()
        self._check_index()
        self._check_search()
        self._check_search_langs()
        return True
