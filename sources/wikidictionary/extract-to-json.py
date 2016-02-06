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
import logging
import os
import xml.etree.ElementTree
import json
from textextract import TextExtract

import sys
sys.path.append('../common/')
from indexcreator import IndexCreator

def init_logging():
    logfile = 'extract-to-json.log'

    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    logger = logging.getLogger('')

def _get_revision_text(revision):
    for child in revision.getchildren():
        if 'text' in child.tag:
            return child.text

    return ''

def _get_username(revision):
    for child in revision.getchildren():
        if 'contributor' in child.tag:
            for uchild in child.getchildren():
                if 'username' in uchild.tag:
                    return uchild.text
    return ''


def to_str(text):
    if type(text) is unicode:
        text = str(text.encode('utf-8'))

    return text

def _get_translation(text, marker):

    label = u''
    start = text.find(marker)
    if start != -1:
        start += len(marker)
        end = text.find('}}', start)
        label = text[start:end]
        label = unicode(label)

    return label


def _show_statistics(stats):
    for stat in stats:
        value = int(stats[stat])
        print ('{0}: {1}'.format(stat, value))

def _save_statistics(stats):

    STATS_FILE = '../stats.json'

    all_stats = None
    with open(STATS_FILE) as data_file:
        all_stats = json.load(data_file)

    stats['date'] = datetime.date.today().strftime("%d/%m/%Y")
    all_stats["wikidictionary"] = stats

    with open(STATS_FILE, 'w') as jsonfile:
        json.dump(all_stats, jsonfile, indent=4)

def read_english_word_list():
    words = list(unicode(line.lower().strip(), 'utf-8') for line in open('../apertium/catalan_words.txt'))
    return words

def term_exists_in_index(index, ca_label, en_label):

    WIKIDICTIONARY = 2
    results = index.search(ca_label)
    for result in results:
        source = result['source']
        if source == WIKIDICTIONARY:
            continue

        idx_ca_label = result['word_ca']
        idx_en_label = result['word_en']
        if idx_en_label is None:
            continue

        if ca_label.lower() == idx_ca_label.lower() and en_label.lower() == idx_en_label.lower():
            return True

    return False
    
    
def _process_xml():
 
    WIKIDICTIONARY = 2
    en_labels = 0
    ca_labels = 0
    fr_labels = 0
    de_labels = 0
    es_labels = 0
    it_labels = 0
    ca_descs = 0
    it_descs = 0
    words = read_english_word_list()

    index = IndexCreator()
    index.open()
    authors = set()
    words_file_ca = open('words-ca.txt','w')
    descriptions_file_ca = open('descriptions-ca.txt','w')
 
    e = xml.etree.ElementTree.parse('cawiktionary-20160111-pages-meta-current.xml').getroot()
    for page in e.getchildren():
        verb = False
        adverbi = False
        adjectiu = False
        en_label = u''
        ca_label = u''
        fr_label = u''
        de_label = u''
        es_label = u''
        it_label = u''

        for page_element in page.getchildren():
            if 'title' in page_element.tag:
                ca_label = unicode(page_element.text)

            if 'revision' in page_element.tag:
                text = _get_revision_text(page_element)
                username = _get_username(page_element)
                if username is not None and len(username) > 0:
                    authors.add(username)

                if text is not None:
                    if '{{ca-verb' in text:
                        verb = True
                    elif '{{lema|ca|adv}}' in text:
                        adverbi = True
                    elif '{{ca-adj' in text:
                        adjectiu = True

                    if verb is True or adverbi is True or adjectiu is True:
                        en_label = _get_translation(text, '{{trad|en|')
                        es_label = _get_translation(text, '{{trad|es|')
                        fr_label = _get_translation(text, '{{trad|fr|')
                        de_label = _get_translation(text, '{{trad|de|')
                        it_label = _get_translation(text, '{{trad|it|')

                        username = _get_username(page_element)
                        if username is not None and len(username) > 0:
                            authors.add(username)
        
        if verb is False and adverbi is False and adjectiu is False:
            continue

        if ca_label.lower().strip() not in words:
            logging.debug("Discard not in word list: " + ca_label)
            continue

        if term_exists_in_index(index, ca_label, en_label):
            logging.debug("Discard already existing word in index: " + ca_label)
            continue

        # TODO: A better way to determine infinitives
        ca_label_str = to_str(ca_label)
        if verb is True and ca_label_str[len(ca_label_str) - 1] != 'r':
            logging.debug("Discard verb is not infinitive: " + ca_label)
            continue

        ca_desc = u''
        textExtract = TextExtract(text)
        s = textExtract.GetDescription()

        if len(en_label) == 0 and len(es_label) == 0 and len(fr_label) == 0 and \
           len(de_label) == 0 and len(it_label) == 0:
            logging.debug("Discard only ca_label:" + ca_label)
            continue

        if len(s) > 0:
            ca_desc = s
            ca_descs += 1

        ca_labels += 1
        if len(en_label) > 0:
            en_labels += 1

        if len(es_label) > 0:
            es_labels += 1

        if len(fr_label) > 0:
            fr_labels += 1

        if len(de_label) > 0:
            de_labels += 1

        if len(it_label) > 0:
            it_labels += 1

        words_file_ca.write(ca_label.encode('utf-8') + '\r\n')

        if ca_desc is not None:
            s = '{0} - {1}\r\n'.format(ca_label.encode('utf-8'), ca_desc.encode('utf-8'))
            descriptions_file_ca.write(s)
   
        index.write_entry(word_en=en_label,
                          word_ca=ca_label,
                          word_fr=fr_label,
                          word_de=de_label,
                          word_es=es_label,
                          word_it=it_label,
                          definition_en=None,
                          definition_ca=ca_desc,
                          definition_fr=None,
                          definition_de=None,
                          definition_es=None,
                          definition_it=None,
                          image=None,
                          permission=None,
                          gec=None,
                          wikidata_id=None,
                          wikiquote_ca=None,
                          wikidictionary_ca=ca_label,
                          source=WIKIDICTIONARY)

    stats = {
             "ca_labels": ca_labels,
             "ca_descs": ca_descs,
             "en_labels": en_labels,
             "fr_labels": fr_labels,
             "de_labels": de_labels,
             "en_labels": en_labels,
             "es_labels": es_labels,
             "it_labels": it_labels
        }

    _show_statistics(stats)
    _save_statistics(stats)
    index.save()
    words_file_ca.close()
    descriptions_file_ca.close()


def main():

    print("Reads a Wikidictionary XML dump and extracts verbs and its translations")
    init_logging()
    start_time = datetime.datetime.now()
    _process_xml()
    msg = 'Time {0}'.format(datetime.datetime.now() - start_time)
    logging.info(msg)


if __name__ == "__main__":
    main()
