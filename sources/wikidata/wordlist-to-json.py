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
import logging
import os
import sys
import json

from pymongo import MongoClient
from mongorecords import MongoRecords
from commonsimage import CommonsImage
from collections import OrderedDict
from claims import Claims

sys.path.append('../common/')
from indexcreator import IndexCreator


def percentage(part, whole):
    return str(100 * float(part)/float(whole))


def _is_segment_valid(string, description):
    # Discard numeric strings only (like years)
    if string.isdigit():
        return False

    if description is not None:
        if 'disambiguation page' in description or \
           'category page' in description or \
           'Wikimedia category' in description:
            return False

    return True

def _create_collection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['local']
    return db

def read_english_word_list():
    words = list(line.lower() for line in open('../apertium/catalan_words.txt'))
    read_list = list(words)
    # All also upper version
    for word in list(read_list):
        word = word[0].upper() + word[1:]
        words.append(word)

    return words

def _show_statistics(stats, json_file):
    cnt = stats["entries"]

    for stat in stats:
        value = int(stats[stat])
        if '_' in stat:
            logging.info('{0}: {1} ({2}%)'.format(stat, value, percentage(value, cnt)))
        else:
            logging.info('{0}: {1}'.format(stat, value))

def _get_image(item):
    claims = item['claims']
    if 'P18' not in claims:
        return None
    try:
        claim = claims['P18']
        return claim[0]['mainsnak']['datavalue']['value']
    except:
        return None

def _get_GEC(item):
    claims = item['claims']
    if 'P1296' not in claims:
        return None
    claim = claims['P1296']
    return claim[0]['mainsnak']['datavalue']['value']

def _get_sitelink(item, link):
    if 'sitelinks' not in item:
        return None

    sitelinks = item['sitelinks']
    if link not in sitelinks:
        return None

    return sitelinks[link]['title']

def init_logging():
    logfile = 'wordlist-to-json.log'

    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger = logging.getLogger('')
    logger.addHandler(ch)

    logger = logging.getLogger('peewee')
    logger.setLevel(logging.ERROR)

def _process_json():

    WIKIDATA = 1
    cnt = 0
    selected = 0
    en_labels = 0
    it_labels = 0
    ca_labels = 0
    fr_labels = 0
    de_labels = 0
    es_labels = 0
  
    en_descs = 0
    ca_descs = 0
    fr_descs = 0
    de_descs = 0
    es_descs = 0
    it_descs = 0
    images = 0
    articles = set()
    index = IndexCreator()
    claims = Claims()

    words_file_en = open('words-en.txt','w')
    words_file_ca = open('words-ca.txt','w')
    json_file = open('wordlist-wikidata.json', 'w')
    db = _create_collection()
    words = read_english_word_list()
    mongo_records = MongoRecords(db)

    index.create()

    for word in words:
        word = word.strip()
        items = mongo_records.findEntry(word)

        if items is None:
            continue

        #if cnt > 50000:
            #break

        for item in items:

            label = item.get('labels')
            if label is None:
                continue

            item_id = item['id']
            if item_id.startswith("Q") is False:
                continue

            if item_id in articles:
                continue

            articles.add(item_id)

            cnt = cnt + 1
            en_label = mongo_records.get_label(label, 'en')
            ca_label = mongo_records.get_label(label, 'ca')
           
            if en_label is None or ca_label is None:
                continue

            fr_label = mongo_records.get_label(label, 'fr')
            de_label = mongo_records.get_label(label, 'de')
            es_label = mongo_records.get_label(label, 'es')
            it_label = mongo_records.get_label(label, 'it')

            descriptions = item.get('descriptions')
            en_description = mongo_records.get_description(descriptions, 'en')
            ca_description = mongo_records.get_description(descriptions, 'ca')
            fr_description = mongo_records.get_description(descriptions, 'fr')
            de_description = mongo_records.get_description(descriptions, 'de')
            es_description = mongo_records.get_description(descriptions, 'es')
            it_description = mongo_records.get_description(descriptions, 'it')

            if _is_segment_valid(en_label, en_description) is False:
                continue

            if claims.valid_claim(ca_label, item) is False:
                continue

            claims.store_claim(item)

            selected = selected + 1
            data = {}
            data['en'] = en_label
            en_labels = en_labels + 1

            if ca_label is not None:
                data['ca'] = ca_label
                ca_labels = ca_labels + 1

            if fr_label is not None:
                data['fr'] = fr_label
                fr_labels = fr_labels + 1

            if de_label is not None:
                data['de'] = de_label
                de_labels = de_labels + 1

            if es_label is not None:
                data['es'] = es_label
                es_labels = es_labels + 1

            if it_label is not None:
                data['it'] = it_label
                it_labels = it_labels + 1

            if en_description is not None:
                data['en_description'] = en_description
                en_descs = en_descs + 1

            if ca_description is not None:
                data['ca_description'] = ca_description
                ca_descs = ca_descs + 1

            if fr_description is not None:
                data['fr_description'] = fr_description
                fr_descs = fr_descs + 1

            if de_description is not None:
                data['de_description'] = de_description
                de_descs = de_descs + 1

            if es_description is not None:
                data['es_description'] = es_description
                es_descs = es_descs + 1

            if it_description is not None:
                data['it_description'] = it_description
                it_descs = it_descs + 1

            image = _get_image(item)

            permission = None
            if image is not None:
                commons_image = CommonsImage(image)
                image, permission = commons_image.get_url_permission()
                if image is not None:
                    data['image'] = image
                    images = images + 1
                if permission is not None:
                    data['permission'] = permission

            gec = _get_GEC(item)
            if gec is not None:
                data['gec'] = gec

            ca_wikiquote = _get_sitelink(item, 'cawikiquote')
            if ca_wikiquote is not None:
                data['wikiquote_ca'] = ca_wikiquote

            data['WikidataId'] = item_id
            json.dump(data, json_file, indent=4, separators=(',', ': '))

            index.write_entry(word_en=en_label,
                             word_ca=ca_label,
                             word_fr=fr_label,
                             word_de=de_label,
                             word_es=es_label,
                             word_it=it_label,
                             definition_en=en_description,
                             definition_ca=ca_description,
                             definition_fr=fr_description,
                             definition_de=de_description,
                             definition_es=es_description,
                             definition_it=it_description,
                             image=image,
                             permission=permission,
                             gec=gec,
                             wikidata_id=item_id,
                             wikiquote_ca=ca_wikiquote,
                             wikidictionary_ca=None,
                             source=WIKIDATA)

            words_file_en.write(en_label.encode('utf-8') + '\r\n')
            words_file_ca.write(ca_label.encode('utf-8') + ' id:' + str(item_id) + '\r\n')
            claims.write_to_wordclaims(ca_label, item_id, item)
                  
    claims.write_claims_stats(mongo_records)

    stats = OrderedDict([
        ("words", len(words)),
        ("entries", cnt),
        ("selected", selected),
        ("ca_labels", ca_labels),
        ("en_labels", en_labels),
        ("it_labels", it_labels),
        ("es_labels", es_labels),
        ("ca_descs", ca_descs),
        ("en_descs", en_descs),
        ("fr_labels", fr_labels),
        ("de_labels", de_labels),
        ("fr_descs", fr_descs),
        ("de_descs", de_descs),
        ("es_descs", es_descs),
        ("it_descs", it_descs),
        ("images", images)
        ])

    _show_statistics(stats, json_file)
    stats['date'] = datetime.date.today().strftime("%d/%m/%Y")
    index.save()
    words_file_en.close()
    words_file_ca.close()

    wiki_stats = {"wikidata": stats}
    with open('../stats.json', 'w') as jsonfile:
        json.dump(wiki_stats, jsonfile, indent=4)

def create_index():
    print ("Index creation started")
    db = _create_collection()
    db.wikidata.ensure_index("labels.ca.value", background=True)
    print ("Index creation completed")
    return


# https://www.mediawiki.org/wiki/Wikibase/DataModel/Primer
def main():

    # Download data set from http://dumps.wikimedia.org/other/wikidata/
    # I tried using commons and mediawiki categories without great results
    # instead we choose a word if this appears on Softcatalà memories.
    print ("Reads a list of English words and generates a JSON file")
    print ("with the entries found in MongoDb with labels and descriptions")

    init_logging()
    start_time = datetime.datetime.now()
    #create_index()
    _process_json()
    msg = 'Time {0}'.format(datetime.datetime.now() - start_time)
    logging.info(msg)


if __name__ == "__main__":
    main()
