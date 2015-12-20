#!/bin/sh
rm -r -f indexdir

cd wikidata
python wordlist-to-json.py
cd ..

cd wikidictionary
python extract-to-json.py
