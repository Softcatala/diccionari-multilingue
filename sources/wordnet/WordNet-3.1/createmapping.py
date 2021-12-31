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

import logging
from urllib.request import Request, urlopen
import fnmatch
import os
import json

def read_synset31_ids():
    with open('../../wordnet31-synset-ids.txt', 'r') as fh:
        lines = fh.readlines()

    return lines


def find(directory, pattern):
    filelist = []

    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                filelist.append(filename)

    filelist.sort()
    return filelist

def get_mapping_keys_30(data):
    for item in data:
        if 'old_keys' not in item:
            continue

        old_keys = item['old_keys']

        if 'pwn30' in old_keys:
            return old_keys['pwn30']


    return []

def get_mapping_keys_31(data):
    for item in data:
        return item['id']

def get_mapping_keys_subject(data):
    for item in data:
        return item['subject']

def main():
    print("Creates a mapping file between Wordnet 3.0 and 3.1 synset ids")

    mappings_written = 0
    with open("wn30-to-31-mapping.txt", 'w') as fh_out:
        for file in find("data/", "*"):
            with open(file, 'r') as fh:
                data = json.load(fh)

                key_31 = get_mapping_keys_31(data)
                keys = get_mapping_keys_30(data)
                if len(keys) == 0:
                    continue

                subject = get_mapping_keys_subject(data)
                for key in keys:
                    fh_out.write(f"{key_31}\t{key}\t{subject}\n")
                    mappings_written += 1

    print(f"Mappings written: {mappings_written}")
        
if __name__ == "__main__":
    main()
