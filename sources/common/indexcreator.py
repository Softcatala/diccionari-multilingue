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

import os
import sys

from whoosh.fields import TEXT, NUMERIC, STORED, Schema
from whoosh.index import *
from whoosh.analysis import StandardAnalyzer
from whoosh.qparser import MultifieldParser
from whoosh.highlight import WholeFragmenter

class IndexCreator(object):

    def __init__(self):
        self.dir_name = "../indexdir"
        self.writer = None
        self.index = None

    def open(self):
        print "Index exists: " + str(exists_in(self.dir_name))
        self.index = open_dir(self.dir_name)
        self.writer = self.index.writer()
        print "Index (open) documents: " + str(self.index.doc_count())
        print "Index (open) last_modified: " + str(self.index.last_modified())

    def _get_first_letter_for_index(self, word_ca):

        s = ''
        if word_ca is None:
            return s

        s = word_ca[0].lower()
        mapping = { u'à' : u'a',
                    u'è' : u'e',
                    u'é' : u'e',
                    u'í' : u'i',
                    u'ó' : u'o',
                    u'ò' : u'o',
                    u'ú' : u'u'} 

        if s in mapping:
            s = mapping[s]

        return s;

    def _get_quality(self, image, gec, wikiquote_ca, wikidictionary_ca):

        quality = 0
        if image is not None and len(image) > 0:
            quality += 1

        if gec is not None and len(gec) > 0:
            quality += 1
 
        if wikiquote_ca is not None and len(wikiquote_ca) > 0:
            quality += 1

        if wikidictionary_ca is not None and len(wikidictionary_ca) > 0:
            quality += 1

        return quality

    def write_entry(self, word_en, word_ca, word_fr, word_de, word_es, word_it,
                    definition_en, definition_ca, definition_fr,
                    definition_de, definition_es, definition_it, image, 
                    permission, gec, wikidata_id, wikiquote_ca, 
                    wikidictionary_ca, source):

        index_letter = self._get_first_letter_for_index(word_ca)

        # As Dec 2015 Wikidata corpus in Catalan was imported in upper case
        # that is incorrect. We fix it here until is fix in upstream
        if word_ca is not None:
            word_ca = word_ca.lower()

        quality = self._get_quality(image, gec, wikiquote_ca, wikidictionary_ca)
        self.writer.add_document(word_en=word_en,
                                 word_ca=word_ca,
                                 word_fr=word_fr,
                                 word_de=word_de,
                                 word_es=word_es,
                                 word_it=word_it,
                                 definition_en=definition_en,
                                 definition_ca=definition_ca,
                                 definition_fr=definition_fr,
                                 definition_de=definition_de,
                                 definition_es=definition_es,
                                 definition_it=definition_it,
                                 image=image,
                                 permission=permission,
                                 gec=gec,
                                 wikidata_id=wikidata_id,
                                 wikiquote_ca=wikiquote_ca,
                                 index_letter=index_letter,
                                 wikidictionary_ca=wikidictionary_ca,
                                 source=source,
                                 quality=quality)

    def save(self):
        self.writer.commit()
        print "Index documents: " + str(self.index.doc_count())
        print "Index last_modified: " + str(self.index.last_modified())

    def create(self):
        analyzer = StandardAnalyzer(minsize=1, stoplist=None)
        schema = Schema(word_en=TEXT(stored=True, sortable=True, analyzer=analyzer),
                        word_ca=TEXT(stored=True, sortable=True, analyzer=analyzer),
                        word_fr=TEXT(stored=True, sortable=True, analyzer=analyzer),
                        word_de=TEXT(stored=True, sortable=True, analyzer=analyzer),
                        word_es=TEXT(stored=True, sortable=True, analyzer=analyzer),
                        word_it=TEXT(stored=True, sortable=True, analyzer=analyzer),
                        definition_en=STORED(),
                        definition_ca=STORED(),
                        definition_fr=STORED(),
                        definition_de=STORED(),
                        definition_es=STORED(),
                        definition_it=STORED(),
                        image=STORED(),
                        permission=STORED(),
                        gec=STORED(),
                        wikidata_id=STORED(),
                        wikiquote_ca=STORED(),
                        index_letter=TEXT(stored=True, analyzer=analyzer),
                        wikidictionary_ca=STORED(),
                        source=NUMERIC(stored=True),
                        quality=NUMERIC(stored=True))

        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)

        self.index = create_in(self.dir_name, schema)

        self.writer = self.index.writer()
        return self.index

    def search(self, word):
        self.searcher = self.index.searcher()
        fields = []
        field = u'word_ca'
        qs = u'{0}:({1})'.format(field, word)
        fields.append(field)

        query = MultifieldParser(fields, self.index.schema).parse(qs)
        results = self.searcher.search(query, limit=None)
        results.fragmenter = WholeFragmenter()
        return results
