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
from pymongo import MongoClient

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

def findEntry(db, entry):
    s = '{0}'.format(entry)
    records = db.wikidata.find({'labels.en.value': s})
    return records

def findClaim(db, claim):
    record = db.wikidata.find_one({'id': '{0}'.format(claim)})
    return record['labels']['en']['value']

def read_english_word_list():
    return set(line.lower() for line in open('../apertium/english_words.txt'))

def get_en_ca_labels(label):
    en_label = label.get('en')
    ca_label = label.get('ca')

    if en_label is not None:
        en_label = en_label.get('value')

    if ca_label is not None:
        ca_label = ca_label.get('value')

    return en_label, ca_label

def get_en_ca_descriptions(description):
    if description is None:
        return None, None

    en_description = description.get('en')
    ca_description = description.get('ca')

    if en_description is not None:
        en_description = en_description.get('value')

    if ca_description is not None:
        ca_description = ca_description.get('value')

    return en_description, ca_description

def _show_statistics(stats, json_file):
    cnt = stats["entries"]
    entries = stats["entries"]
    words = stats["words"]
    entries = stats["entries"]
    selected = stats["selected"]
    ca_labels = stats["ca_labels"]
    en_labels = stats["en_labels"]
    ca_descs = stats["ca_descs"]
    en_descs = stats["en_descs"]

    print ("Total words: " + str(words))
    print ("Total entries: " + str(entries))
    print ("Selected: {0} ({1}%)".format(str(selected), str(percentage(selected, cnt))))
    print ("ca labels: {0} ({1}%)".format(str(ca_labels), str(percentage(ca_labels, cnt))))
    print ("en labels: {0} ({1}%)".format(str(en_labels), str(percentage(en_labels, cnt))))
    print ("ca descriptions: {0} ({1}%)".format(str(ca_descs), str(percentage(ca_descs, cnt))))
    print ("en descriptions: {0} ({1}%)".format(str(en_descs), str(percentage(en_descs, cnt))))

    json.dump(stats, json_file, indent=4, separators=(',', ': '))

def _process_json():

    cnt = 0
    selected = 0
    en_labels = 0
    ca_labels = 0
    en_descs = 0
    ca_descs = 0

    json_file = open('worldlist-wikidata.json', 'w')
    db = _create_collection()
    words = read_english_word_list()

    for word in words:
        word = word.strip()
        items = findEntry(db, word)

        if items is None:
            if len(word) > 2:
                word = word[0].upper() + word[1:]
                items = findEntry(db, word)

        if items is None:
            continue

        for item in items:

            label = item.get('labels')
            if label is None:
                continue

            item_id = item['id']
            if item_id.startswith("Q") is False:
                continue

            cnt = cnt + 1
            en_label, ca_label = get_en_ca_labels(label)

            if en_label is None:
                en_label += en_label + 1
                continue

            if _is_segment_valid(en_label) is False:
                continue

            descriptions = item.get('descriptions')
            en_description, ca_description = get_en_ca_descriptions(descriptions)

            selected = selected + 1
            data = {}
            data['en'] = en_label
            en_labels = en_labels + 1

            if ca_label is None:
                data['ca'] = ca_label
                ca_labels = ca_labels + 1

            if en_description is not None:
                data['en_description'] = en_description
                en_descs = en_descs + 1

            if ca_description is not None:
                data['ca_description'] = ca_description
                ca_descs = ca_descs + 1

            data['comment'] = item_id
            json.dump(data, json_file, indent=4, separators=(',', ': '))

    stats = {
        "words": len(words),
        "entries": cnt,
        "selected": selected,
        "ca_labels": ca_labels,
        "en_labels": en_labels,
        "ca_descs": ca_descs,
        "en_descs": en_descs
    }

    _show_statistics(stats, json_file)

def create_index():
    db = _create_collection()
    db.wikidata.create_index("labels.en.value")
    print "End"
    return


# https://www.mediawiki.org/wiki/Wikibase/DataModel/Primer
def main():

    # Download data set from http://dumps.wikimedia.org/other/wikidata/
    # I tried using commons and mediawiki categories without great results
    # instead we choose a word if this appears on Softcatalà memories.
    print ("Reads a list of English words and generates a JSON file")
    print ("with the entries found in MongoDb with label and description")

    start_time = datetime.datetime.now()
    _process_json()
    print ('Time {0}'.format(datetime.datetime.now() - start_time))

if __name__ == "__main__":
    main()
