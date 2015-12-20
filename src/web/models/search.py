#!/usr/bin/env python
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

from whoosh.highlight import WholeFragmenter
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
import json
import cgi

class Search(object):
    """Search a term in the Whoosh index."""
    dir_name = "indexdir"

    def __init__(self, word_ca):
        self._word_ca = word_ca
        self.searcher = None
        self.query = None
        self.Index = False
        self.Duplicates = True
        self.AutoComplete = False

    @property
    def has_invalid_search_term(self):
        return self.word_ca is None

    @property
    def word_ca(self):
        return self._word_ca

    def get_results(self):
        if self.searcher is None:
            self.search()

        if self.Index is True or self.AutoComplete is True:
            results = self.searcher.search(self.query,
                                           limit=None,
                                           sortedby='word_ca',
                                           collapse_limit=1,
                                           collapse='word_ca')
        else:
            results = self.searcher.search(self.query, limit=None)

        results.fragmenter = WholeFragmenter()
        return results

    def search(self, ix=None):
        if ix is None:
            ix = open_dir(self.dir_name)
            self.search(ix)

        self.searcher = ix.searcher()
        fields = []
        qs = ''

        # We use parenthesis to prevent operators like OR used in source
        # to affect target
        if self.Index is True:
            if self.word_ca is not None and len(self.word_ca) > 0:
                qs += u' index_letter:({0})'.format(self.word_ca)
                fields.append("index_letter")
        else:
            if self.word_ca is not None and len(self.word_ca) > 0:
                qs += u' word_ca:({0})'.format(self.word_ca)
                fields.append("word_ca")

        self.query = MultifieldParser(fields, ix.schema).parse(qs)

    def get_json(self):
        results = self.get_results()
        all_results = []
        if self.Index is False:
            results = results[:10]

        words = []
        for result in results:
            if self.AutoComplete is True or self.Index:
                words.append(result['word_ca'])
            else:
                all_results.append(self.get_result(result))

        if self.AutoComplete is True or self.Index:
            all_results.append({"words" : words})

        return json.dumps(all_results, indent=4, separators=(',', ': '))


    def _get_result(self, result, key):
        if key in result:
            return cgi.escape(result[key]) 

        return None

    def get_result(self, result):
        image = self._get_result(result, "image")
        if 'permission' in result:
            permission = result["permission"]
        else:
            permission = None

        definition_ca = self._get_result(result, "definition_ca")
    
        result_dict = {
            'word_ca': self._get_result(result, "word_ca"),
            'definition_ca' : definition_ca,
            'word_en': self._get_result(result, "word_en"),
            'definition_en' : self._get_result(result, "definition_en"),
            'word_fr': self._get_result(result, "word_fr"),
            'definition_fr' : self._get_result(result, "definition_fr"),
            'word_de': self._get_result(result, "word_de"),
            'definition_de' : self._get_result(result, "definition_de"),
            'word_es': self._get_result(result, "word_es"),
            'definition_es' : self._get_result(result, "definition_es"),
            'image' : image,
             #'permission' : permission,
            'gec' : self._get_result(result, "gec"),
            'wikidata_id' : self._get_result(result, "wikidata_id"),
            'ca_wikiquote' : self._get_result(result, "ca_wikiquote"),
            'ca_wikidictionary' : self._get_result(result, "ca_wikidictionary"),
        }

        return result_dict

