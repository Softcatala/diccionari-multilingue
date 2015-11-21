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

def to_str(text):
    if type(text) is unicode:
        text = str(text.encode('utf-8'))

    return text

def _process_xml():
 
    e = xml.etree.ElementTree.parse('cawiktionary-20151102-pages-meta-current.xml').getroot()
    for page in e.getchildren():
        title = ''
        verb = False
        en_label = ''
        for page_element in page.getchildren():
            if 'title' in page_element.tag:
                title = to_str(page_element.text)

            if 'revision' in page_element.tag:
                text = _get_revision_text(page_element)
                if text is not None:
                    if '{{ca-verb' in text:
                        verb = True

                        EN_MARKER = '{{trad|en|'
                        start = text.find(EN_MARKER)
                        if start != -1:
                            start += len(EN_MARKER)
                            end = text.find('}}', start)
                            en_label = text[start:end]
                            en_label = to_str(en_label)

        if verb is True:
            # TODO: A better way to determine infinitives
            if title[len(title) - 1] == 'r':
                print "ca:" + title
                if len(en_label) > 0:
                    print "en:" + en_label
                print ""

def main():

    print ("Reads a Wikidictionary XML dump")

    init_logging()
    start_time = datetime.datetime.now()
    _process_xml()
    msg = 'Time {0}'.format(datetime.datetime.now() - start_time)
    logging.info(msg)


if __name__ == "__main__":
    main()
