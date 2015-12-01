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
    
def _process_xml():
 
    en_labels = 0
    ca_labels = 0
    fr_labels = 0
    de_labels = 0
    es_labels = 0

    index = IndexCreator()
    index.open()
    authors = set()

    e = xml.etree.ElementTree.parse('cawiktionary-20151102-pages-meta-current.xml').getroot()
    for page in e.getchildren():
        verb = False
        en_label = u''
        ca_label = u''
        fr_label = u''
        de_label = u''
        es_label = u''

        for page_element in page.getchildren():
            if 'title' in page_element.tag:
                ca_label = unicode(page_element.text)

            if 'revision' in page_element.tag:
                text = _get_revision_text(page_element)
                username = _get_username(page_element)
                if username is not None and len(username) > 0:
                    print username
                    authors.add(username)
    
                if text is not None:
                    if '{{ca-verb' in text:
                        verb = True
                        en_label = _get_translation(text, '{{trad|en|')
                        es_label = _get_translation(text, '{{trad|es|')
                        fr_label = _get_translation(text, '{{trad|fr|')
                        de_label = _get_translation(text, '{{trad|de|')

                        username = _get_username(page_element)
                        if username is not None and len(username) > 0:
                            authors.add(username)


        if verb is True:
            # TODO: A better way to determine infinitives
            ca_label_str = to_str(ca_label)
            if ca_label_str[len(ca_label_str) - 1] == 'r':
                ca_labels += 1
                #print "ca:" + ca_label
                if len(en_label) > 0:
                    #print "en:" + en_label
                    en_labels += 1

                if len(es_label) > 0:
                    #print "es:" + es_label
                    es_labels += 1

                if len(fr_label) > 0:
                    #print "fr:" + fr_label
                    fr_labels += 1

                if len(de_label) > 0:
                    #print "de:" + de_label
                    de_labels += 1

                wikidict_url = u'{0}/{1}'.format('', ca_label)

                index.write_entry(word_en=en_label,
                 word_ca=ca_label,
                 word_fr=fr_label,
                 word_de=de_label,
                 word_es=es_label,
                 definition_en=None,
                 definition_ca=None,
                 definition_fr=None,
                 definition_de=None,
                 definition_es=None,
                 image=None,
                 permission=None,
                 gec=None,
                 wikidata_id=None,
                 ca_wikiquote=None,
                 ca_wikidictionary=ca_label)

    stats = {
        "ca_labels" : ca_labels,
        "en_labels" : en_labels,
        "fr_labels" : fr_labels,
        "de_labels" : de_labels,
        "en_labels" : en_labels,
        "es_labels" : es_labels
        }

    _show_statistics(stats)
    _save_statistics(stats)
    index.save()

    #print("Authors ---")
    #for author in authors:
    #    print author

def main():

    print("Reads a Wikidictionary XML dump and extracts verbs and its translations")
    init_logging()
    start_time = datetime.datetime.now()
    _process_xml()
    msg = 'Time {0}'.format(datetime.datetime.now() - start_time)
    logging.info(msg)


if __name__ == "__main__":
    main()
