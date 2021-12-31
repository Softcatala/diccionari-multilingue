#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import json
import sys
import ijson

def save(values, append = False):
    with open('terms.json', 'w') as outfile:
        json.dump(values, outfile, skipkeys=True, indent=4, ensure_ascii=False)

def _load_wikidata():

    id_item = {}
    fh = open('wikidata/terms.json', 'r')
    items = ijson.items(fh, 'item', use_float=True)        

    return items

def _load_wordnet():
    with open('wordnet/terms.json', 'r') as fh:
        wordnet = json.load(fh)

    print(f"Wordnet read {len(wordnet)} items")
    return wordnet


def _wordnet_todict(wordnet):
    id_item = {}
    for item in wordnet:
        id = item['id']
        new_id = item['id'][1:] + "-" + item['id'][0:1]
        item['id'] = new_id
        id_item[new_id] = item

    return id_item


def get_synset_id(item):
    
    synset_id = None

    property_keys = item['claims']['P8814']
#    print(data['datavalue']['value'])
    #['datavalue']['value']
    for property_key in property_keys:
#        print("key: " + str(property_key))
        if 'mainsnak' not in property_key:
            continue

        synset_id = property_key['mainsnak']['datavalue']['value']
        break

    return synset_id

def get_label_description(item, language):
    label = ''
    description = ''

    try:
        label = item['labels'][language]['value']
        if language in item['descriptions']:
            description = item['descriptions'][language]['value']
        
    except:
        pass

    return label, description


def _wikidata_todict(items):
    id_item = {}
    
    for item in items:
        en_label, en_description = get_label_description(item, 'en')
        synset_id = get_synset_id(item)

        new_item = {}

        label, description = get_label_description(item, 'en')
        new_item['en_label'] = label
        new_item['en_description'] = description

        label, description = get_label_description(item, 'ca')
        new_item['ca_label'] = label
        new_item['ca_description'] = description

        label, description = get_label_description(item, 'es')
        new_item['es_label'] = label
        new_item['es_description'] = description
        new_item['id'] = synset_id

        id_item[synset_id] = new_item

    return id_item

def show_item(item):

    print(f"--- {item['id']} ")
    print(item['en_label'])
    print(item['en_description'])

    print(item['ca_label'])
    print(item['ca_description'])

    print(item['es_label'])
    print(item['es_description'])


def main():
 #    wordnet_list = _load_wordnet()
 #   wordnet_dict = _wordnet_todict(wordnet_list)
    wikidata = _load_wikidata()
    wikidata_dict = _wikidata_todict(wikidata)

#    wikidata_dict = _load_wikidata()

    items_found = 0

    with open('wordnet31-synset-ids.txt', 'w') as wordnet31_fh:

        for synset_id in wikidata_dict:
            #if synset_id not in wordnet_dict:
            #    continue

            show_item(wikidata_dict[synset_id])
            #print(f"{wikidata_dict[synset_id]}")
            #print(f"wordnet: {wordnet_dict[synset_id]}")
            items_found += 1
            wordnet31_fh.write(synset_id + "\n")

    print(f"items_found: {items_found}")
    
if __name__ == "__main__":
    print("Merge sources")
    main()
