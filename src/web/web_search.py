#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2014-2015 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from flask import Flask, request, Response
import cgi
import time
import sys
import urllib
import json
import itertools
from jinja2 import Environment, FileSystemLoader
from urlparse import urlparse
from webview import WebView
from indexview import IndexView

sys.path.append('models/')
from pagination import Pagination
from search import Search


app = Flask(__name__)


@app.route('/')
def search_request():
    source = request.args.get('source')
    search = Search(source)
    View = WebView()
    result = View.do(search)
    return result

def set_stats_sum_for(values, value):
    #values[value] = values['wikidata'][value] + values['wikidictionary'][value] 
    result = values['wikidata'][value]
    if value in values['wikidictionary']:
        result += values['wikidictionary'][value]

    values[value] = result

@app.route('/api/statistics')
def api_statistics():
    STATS_FILE = 'stats.json'
    with open(STATS_FILE) as data_file:    
        values = json.load(data_file)

    values = json.dumps(values, indent=4)
    return Response(values, mimetype='application/json')

@app.route('/api/autocomplete/<word>', methods=['GET'])
def autocomplete_api(word):
    search = Search(word + u"*")
    search.AutoComplete = True
    return Response(search.get_json(), mimetype='application/json')

@app.route('/api/search/<word>', methods=['GET'])
def search_api(word):
    search = Search(word)
    return Response(search.get_json(), mimetype='application/json')

@app.route('/api/index/<lletra>', methods=['GET'])
def index_letter_api(lletra):
    search = Search(lletra)
    search.Index = True
    search.Duplicates = False
    return Response(search.get_json(), mimetype='application/json')

@app.route('/render/statistics')
def render_statistics():
    
    STATS_FILE = 'stats.json'

    values = None
    with open(STATS_FILE) as data_file:    
        values = json.load(data_file)

    values_to_sum = ['ca_labels', 'fr_labels', 'de_labels', 'en_labels', 'es_labels',
    'ca_descs', 'fr_descs', 'de_descs', 'en_descs', 'es_descs']

    for value in values_to_sum:
        set_stats_sum_for(values, value)
 
    env = Environment(loader=FileSystemLoader('./'))
    template = env.get_template('templates/statistics.html')
    r = template.render(values).encode('utf-8')
    return r

@app.route('/lletra/<lletra>')
def dict_index(lletra):
    start = lletra.find('?')
    if start != -1:
        lletra = lletra[:start]

    search = Search(lletra)
    search.Index = True
    search.Duplicates = False
    View = IndexView(lletra)
    result = View.do(search)
    return result
    

if __name__ == '__main__':
    app.debug = True
    app.run()
