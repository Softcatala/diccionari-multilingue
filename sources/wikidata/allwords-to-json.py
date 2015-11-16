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

import datetime
import json
import operator
from pymongo import MongoClient
from mongorecords import MongoRecords


def percentage(part, whole):
    return 100 * float(part)/float(whole)


def _is_segment_valid(string):
    # Discard numeric strings only (like years)
    if string.isdigit():
        return False

    return True


def _create_collection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['local']
    return db

def _show_statistics(stats, json_file):
    cnt = stats["entries"]
    entries = stats["entries"]
    selected = stats["selected"]
    ca_labels = stats["ca_labels"]
    en_labels = stats["en_labels"]
    ca_descs = stats["ca_descs"]
    en_descs = stats["en_descs"]

    print ("Total entries: " + str(entries))
    print ("Selected: {0} ({1}%)".format(str(selected), str(percentage(selected, cnt))))
    print ("ca labels: {0} ({1}%)".format(str(ca_labels), str(percentage(ca_labels, cnt))))
    print ("en labels: {0} ({1}%)".format(str(en_labels), str(percentage(en_labels, cnt))))
    print ("ca descriptions: {0} ({1}%)".format(str(ca_descs), str(percentage(ca_descs, cnt))))
    print ("en descriptions: {0} ({1}%)".format(str(en_descs), str(percentage(en_descs, cnt))))

    json.dump(stats, json_file, indent=4, separators=(',', ': '))


def _write_claims(mongo_records, claims_stats):
    claims = open('claims.txt', 'w')
    sorted_keys = sorted(claims_stats.items(), key=operator.itemgetter(1), reverse=True)
    for item in sorted_keys:
        mean = mongo_records.findClaim(item[0])
        claims.write('{0}({1}) = {2}\n'.format(item[0], mean.encode('utf-8'), str(item[1])))

    claims.close()

def _excluded_claims(claims):

    excluded_list = {"P1566",
               "P301",
               "P19"
    }

    for excluded in excluded_list:
        if excluded in claims:
            return True 

    return False


def _process_json():

    cnt = 0
    selected = 0
    en_labels = 0
    ca_labels = 0
    en_descs = 0
    ca_descs = 0
    claims_stats = {}
    ca_labels_text = []

    json_file = open('allwords-wikidata.json', 'w')
    db = _create_collection()
    mongo_records = MongoRecords(db)

    items = db.wikidata.find({})

    for item in items:

        label = item.get('labels')
        if label is None:
            continue

        item_id = item['id']
        if item_id is None:
            print "Item id is None"
            continue

        if item_id.startswith("Q") is False:
            continue

        cnt = cnt + 1
        en_label, ca_label = mongo_records.get_en_ca_labels(label)

        if en_label is None:
            continue

        if _is_segment_valid(en_label) is False:
            continue

        descriptions = item.get('descriptions')
        en_description, ca_description = mongo_records.get_en_ca_descriptions(descriptions)

        if ca_label is None or ca_description is None:
            continue

        if en_description is not None:
            if "disambiguation page" in en_description or \
               "template" in en_description or \
               "category" in en_description:
                continue

        data = {}
        data['en'] = en_label
        en_labels = en_labels + 1

        if ca_label is not None:
            data['ca'] = ca_label
            ca_labels = ca_labels + 1

        if en_description is not None:
            data['en_description'] = en_description
            en_descs = en_descs + 1

        if ca_description is not None:
            data['ca_description'] = ca_description
            ca_descs = ca_descs + 1

        data['comment'] = item_id

        claims = item.get('claims')

        if _excluded_claims(claims):
            continue

        if claims is not None:
            text = ''
            for claim in claims:
                text += claim + " "
                times = claims_stats.get(claim)
                if times is None:
                    times = 0
                
                times = times + 1
                claims_stats[claim] = times

            data['claims'] = text

        ca_labels_text.append(ca_label)
        selected = selected + 1
        json.dump(data, json_file, indent=4, separators=(',', ': '))
        #print selected

        #if selected > 100:
        #    break

    _write_claims(mongo_records, claims_stats)

    sorted_keys = sorted(ca_labels_text)
    words = open('words.txt', 'w')
    for item in sorted_keys:
        words.write('{0}\n'.format(item.encode('utf-8')))

    words.close()

    stats = {
        "entries": cnt,
        "selected": selected,
        "ca_labels": ca_labels,
        "en_labels": en_labels,
        "ca_descs": ca_descs,
        "en_descs": en_descs
    }
    _show_statistics(stats, json_file)


def create_index():
    print "Index creation started"
    db = _create_collection()
    db.wikidata.ensure_index("labels.en.value", background=True)
    db.wikidata.ensure_index("id", background=True)
    print "Index creation completed"
    return


# https://www.mediawiki.org/wiki/Wikibase/DataModel/Primer
def main():

    # Download data set from http://dumps.wikimedia.org/other/wikidata/
    # I tried using commons and mediawiki categories without great results
    # instead we choose a word if this appears on Softcatalà memories.
    print ("Reads all the Wikidata entries from Mongo and generates a JSON")

    create_index()
    start_time = datetime.datetime.now()
    _process_json()
    print ('Time {0}'.format(datetime.datetime.now() - start_time))

if __name__ == "__main__":
    main()
