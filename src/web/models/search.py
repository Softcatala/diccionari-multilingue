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


class Search(object):
    """Search a term in the Whoosh index."""
    dir_name = "indexdir"

    def __init__(self, word_ca):
        self._word_ca = word_ca
        self.searcher = None
        self.query = None
        self.Index = False

    @property
    def has_invalid_search_term(self):
        return self.word_ca is None

    @property
    def word_ca(self):
        return self._word_ca

    def get_results(self):
        if self.searcher is None:
            self.search()

        results = self.searcher.search(self.query, limit=None, sortedby='word_ca')
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

