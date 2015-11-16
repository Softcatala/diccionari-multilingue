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

from whoosh.fields import BOOLEAN, TEXT, Schema
from whoosh.index import create_in


class IndexCreator(object):

    def __init__(self):
        self.dir_name = "indexdir"
        self.writer = None

    def write_entry(self, word_en, word_ca, word_fr, word_de, word_es,
                    definition_en, definition_ca, definition_fr, 
                    definition_de, definition_es, image):

        self.writer.add_document(word_en=word_en,
                                 word_ca=word_ca,
                                 word_fr=word_fr,
                                 word_de=word_de,
                                 word_es=word_es,
                                 definition_en=definition_en,
                                 definition_ca=definition_ca,
                                 definition_fr=definition_fr,
                                 definition_de=definition_de,
                                 definition_es=definition_es,
                                 image=image)

    def save(self):
        self.writer.commit()

    def create(self):
        schema = Schema(word_en=TEXT(stored=True),
                        word_ca=TEXT(stored=True),
                        word_fr=TEXT(stored=True),
                        word_de=TEXT(stored=True),
                        word_es=TEXT(stored=True),
                        definition_en=TEXT(stored=True),
                        definition_ca=TEXT(stored=True),
                        definition_fr=TEXT(stored=True),
                        definition_de=TEXT(stored=True),
                        definition_es=TEXT(stored=True),
                        image=TEXT(stored=True))

        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)

        ix = create_in(self.dir_name, schema)

        self.writer = ix.writer()
        return ix
