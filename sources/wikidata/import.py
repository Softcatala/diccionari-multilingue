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

import ijson
import json
import sys

def save(values, append = False):
    with open('terms.json', 'w') as outfile:
        json.dump(values, outfile, skipkeys=True, indent=4, ensure_ascii=False)

def get_en_label_description(item):
    label = ''
    description = ''

    try:
        label = item['labels']['en']['value']
        if 'en' in item['descriptions']:
            description = item['descriptions']['en']['value']
        
    except:
        pass

    return label, description

def main():

    print("")
    items_processed = 0
    items_saved = 0
    total_items = 96386518
    
    with open('words.txt', 'w') as fh_words:
        items = ijson.items(sys.stdin, 'item', use_float=True)

        values = []
        for item in items:
            claims = item['claims']    
            if 'P8814' in claims:
                values.append(item)
                items_saved += 1
                en_label, en_description = get_en_label_description(item)
    
                if en_label is None:
                    continue

                text =f"{en_label} - {en_description}"
#                print(text)
                fh_words.write(text + "\n")

            items_processed += 1

            if items_processed % 1000000 == 0:
                psaved = items_saved * 100 / items_processed
                pprocessed = items_processed * 100 / total_items
                print(f"Items processed {items_processed} ({pprocessed:.2f}%), saved {items_saved} ({psaved:.2f}%)")
                save(values)

if __name__ == "__main__":
    main()
