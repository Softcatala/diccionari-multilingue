#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
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

import logging
import operator

class Claims():

    def __init__(self):
        self.claims_stats = {}
        self.words_claims_file = open('words-claims.txt','w')
        self.previous_claims = self.read_claims()

    def write_claims_stats(self, mongo_records):
        claims = open('claims.txt', 'w')
        sorted_keys = sorted(self.claims_stats.items(), key=operator.itemgetter(1), reverse=True)
        for item in sorted_keys:
            mean = mongo_records.findClaim(item[0])
            claims.write('{0}({1}) = {2}\n'.format(item[0], mean.encode('utf-8'), str(item[1])))

        claims.close()

    def store_claim(self, item):
        claims = item.get('claims')
        if claims is None:
            return

        text = ''
        for claim in claims:
            text += claim + " "
            times = self.claims_stats.get(claim)
            if times is None:
                times = 0
            
            times = times + 1
            self.claims_stats[claim] = times

    def read_claims(self):
        claims = {}
        f = open('claims.txt', 'r')
        while True:
            line = f.readline()
            if line is None or len(line) == 0:
                break

            i = line.find('(')
            claims[line[0:i]] = line

        return claims

    def write_to_wordclaims(self, ca_label, item_id, item):
        if ca_label is None:
            return

        self.words_claims_file.write(ca_label.encode('utf-8') + ' id:' + str(item_id) + '\r\n')
        claims = item.get('claims')
        if claims is None:
            return;

        for claim in claims:
            desc = self.previous_claims[claim]
            text = ' ' + desc
            self.words_claims_file.write(text)


    def valid_claim(self, ca_label, item):
        claims = item.get('claims')
        if claims is None:
            return;

        not_valid = ['P1566', # Geonames
                     'P625', # coordinate location
                     'P345', # IMDb identifier
                     'P577', # Publication date (comics, books, etc)
                     'P106' # Ocupation
                    ]
        for prop in not_valid:
            if prop in claims:
                logging.debug('Discarded {0} because property {1}'.format(ca_label.encode('utf-8'), prop))
                return False

        return True

