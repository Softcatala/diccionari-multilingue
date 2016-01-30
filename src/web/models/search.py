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

    def __init__(self, word, lang = "ca"):
        self._word = word
        self.searcher = None
        self.query = None
        self.Index = False
        self.Duplicates = True
        self.AutoComplete = False
        self.field = self._get_field(lang)

    def _get_field(self, lang):
        mapping = {
            "ca" : "word_ca",
            "en" : "word_en",
            "fr" : "word_fr",
            "es" : "word_es",
            "it" : "word_it",
            "de" : "word_de"
        }

        return mapping[lang]

    @property
    def has_invalid_search_term(self):
        return self.word is None

    @property
    def word(self):
        return self._word

    def get_results(self):
        if self.searcher is None:
            self.search()

        if self.Index is True:
            results = self.searcher.search(self.query,
                                           limit=None,
                                           sortedby='word_ca',
                                           collapse_limit=1,
                                           collapse='word_ca')
        elif self.AutoComplete is True:
            results = self.searcher.search(self.query,
                                           limit=None,
                                           sortedby=self.field,
                                           collapse_limit=1,
                                           collapse=self.field)
        else:
            results = self.searcher.search(self.query, limit=None, sortedby='quality', reverse=True)

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
            if self.word is not None and len(self.word) > 0:
                qs += u' index_letter:({0})'.format(self.word)
                fields.append("index_letter")
        else:
            if self.word is not None and len(self.word) > 0:
                qs += u' {0}:({1})'.format(self.field, self.word)
                fields.append(self.field)

        self.query = MultifieldParser(fields, ix.schema).parse(qs)

    def get_json(self):
        if self.AutoComplete is True or self.Index is True:
            return self._get_json_index_autocomplete()
        else:
            return self._get_json_search()

    def _get_json_search(self):
        wordl = self.word.lower()
        results = self.get_results()
        all_results = []

        for result in results:
            # Whoosh returns any document containg the word. For example, for 
            # 'lluna' contains 'lluna de mel' but we only want exact matches
            if result[self.field].lower() == wordl:
                all_results.append(self.get_result(result))

        return json.dumps(all_results, indent=4, separators=(',', ': '))

    def _get_json_index_autocomplete(self):
        results = self.get_results()
        all_results = []
        if self.Index is False:
            results = results[:10]

        words = []
        for result in results:
            words.append(result[self.field])

        all_results = {}
        all_results["words"] = words
        return json.dumps(all_results, indent=4, separators=(',', ': '))

    def _get_result(self, result, key):
        if key in result:
            return cgi.escape(result[key]) 

        return None

    def add_to_dict(self, dictionary, key, value):
        if value is None or len(value) == 0:
            return

        dictionary[key] = value

    def get_result(self, result):
        image = self._get_result(result, "image")
        if 'permission' in result:
            permission = result["permission"]
        else:
            permission = None

        definition_ca = self._get_result(result, "definition_ca")

        references = {}
            
        self.add_to_dict(references, 'gec', self._get_result(result, "gec"))
        self.add_to_dict(references, 'wikidata', self._get_result(result, "wikidata_id"))
        self.add_to_dict(references, 'wikiquote_ca', self._get_result(result, "wikiquote_ca"))
        self.add_to_dict(references, 'wikidictionary_ca', self._get_result(result, "wikidictionary_ca"))

        if result['source'] == 1:
            source = 'wikidata'
        else:
            source = 'wikidictionary_ca'
    
        result_dict = {}

        self.add_to_dict(result_dict, 'word_ca', self._get_result(result, "word_ca"))
        self.add_to_dict(result_dict, 'definition_ca', definition_ca)
        self.add_to_dict(result_dict, 'word_en', self._get_result(result, "word_en"))
        self.add_to_dict(result_dict, 'definition_en', self._get_result(result, "definition_en"))
        self.add_to_dict(result_dict, 'word_fr', self._get_result(result, "word_fr"))
        self.add_to_dict(result_dict, 'definition_fr', self._get_result(result, "definition_fr"))
        self.add_to_dict(result_dict, 'word_de', self._get_result(result, "word_de"))
        self.add_to_dict(result_dict, 'definition_de', self._get_result(result, "definition_de"))
        self.add_to_dict(result_dict, 'word_es', self._get_result(result, "word_es"))
        self.add_to_dict(result_dict, 'definition_es', self._get_result(result, "definition_es"))
        self.add_to_dict(result_dict, 'word_it', self._get_result(result, "word_it"))
        self.add_to_dict(result_dict, 'definition_it', self._get_result(result, "definition_it"))
        self.add_to_dict(result_dict, 'image', image)
        self.add_to_dict(result_dict, 'references', references)
        self.add_to_dict(result_dict, 'source', source)
        result_dict['quality'] = result['quality']
        return result_dict

