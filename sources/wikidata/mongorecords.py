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


class MongoRecords():

    def __init__(self, db):
        self.db = db

    def findEntry(self, entry):
        s = '{0}'.format(entry)
        records = self.db.wikidata.find({'labels.en.value': s})
        return records

    def findClaim(self, claim):
        record = self.db.wikidata.find_one({'id': '{0}'.format(claim)})
        try:
            return record['labels']['en']['value']
        except:
            return ''

    def get_en_ca_labels(self, label):
        en_label = label.get('en')
        ca_label = label.get('ca')

        if en_label is not None:
            en_label = en_label.get('value')

        if ca_label is not None:
            ca_label = ca_label.get('value')

        return en_label, ca_label

    def get_label(self, label, language):
        label = label.get(language)

        if label is not None:
            label = label.get('value')

        return label

    def get_en_ca_descriptions(self, description):
        if description is None:
            return None, None

        en_description = description.get('en')
        ca_description = description.get('ca')

        if en_description is not None:
            en_description = en_description.get('value')

        if ca_description is not None:
            ca_description = ca_description.get('value')

        return en_description, ca_description

    def get_description(self, description, language):
        if description is None:
            return None

        description = description.get(language)

        if description is not None:
            description = description.get('value')

        return description
