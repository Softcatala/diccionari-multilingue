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
import sys
import json
from jinja2 import Environment, FileSystemLoader
from webview import WebView
from indexview import IndexView

sys.path.append('models/')
from search import Search
from statssql import Stats


app = Flask(__name__)


@app.route('/')
def search_request():
    source = request.args.get('source')
    search = Search(source)
    View = WebView()
    result = View.do(search)
    return result

def set_stats_sum_for(values, value):
    result = values['wikidata'][value]
    if value in values['wikidictionary']:
        result += values['wikidictionary'][value]

    values[value] = result

# API calls
def json_answer(data):
    resp = Response(data, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

def json_answer_status(data, status):
    resp = json_answer(data)
    resp.status = str(status)
    return resp

@app.route('/statistics')
def api_statistics():
    STATS_FILE = 'stats.json'
    with open(STATS_FILE) as data_file:
        values = json.load(data_file)

    values = json.dumps(values, indent=4)
    return json_answer(values)

@app.route('/autocomplete/<word>', methods=['GET'])
def autocomplete_api(word):
    word = word + u"*" 
    lang = request.args.get('lang')
    if lang is None:
        search = Search(word)
    else:
        search = Search(word, lang)

    search.AutoComplete = True
    return json_answer(search.get_json())

def save_stats(word, lang):
    if lang is None:
        lang = 'ca'

    Stats.create_table(fail_silently=True)

    try:
        result = Stats.select().where((Stats.word==word) & (Stats.lang==lang)).get()

    except:
        result = None

    if result is not None:
        result.times = result.times + 1
        result.save()
    else:
        times = 1
        stats = Stats(word = word, lang = lang, times = times)
        stats.save()

@app.route('/usage', methods=['GET'])
def usage_api():

    out = 'Tracking enabled: {0}<br/><br/>'.format(str(is_tracking_enabled()))
    results = Stats.select().order_by(Stats.times.desc())
    for result in results:
        word = result.word.encode('utf-8')
        msg = '{0} - {1} - {2}<br/>'.format(word, result.lang, result.times)
        out += msg

    return out

@app.route('/search/<word>', methods=['GET'])
def search_api(word):
    lang = request.args.get('lang')
    it = request.args.get('it')
    if lang is None:
        search = Search(word)
    else:
        search = Search(word, lang)

    if it is None and is_tracking_enabled():
        save_stats(word, lang)

    j, status = search._get_json_search()
    if status == 404:
        j = json.dumps([], indent=4, separators=(',', ': '))
        return json_answer(j)

    return json_answer_status(j, status)

@app.route('/index/<lletra>', methods=['GET'])
def index_letter_api(lletra):
    search = Search(lletra)
    search.Index = True
    search.Duplicates = False
    return json_answer(search.get_json())

def is_tracking_enabled():
    enable = False
    try:
        f = open('tracking.txt','r')
        line = f.readline()
        f.close()
        status = int(line)
        if status == 1:
            enable = True
    except:
        pass

    return enable


@app.route('/track/<enable>', methods=['GET'])
def track_api(enable):
    f = open('tracking.txt','w')
    f.write(enable)
    f.close()
    return str(is_tracking_enabled())

# Render calls
@app.route('/render/statistics')
def render_statistics():

    STATS_FILE = 'stats.json'

    values = None
    with open(STATS_FILE) as data_file:
        values = json.load(data_file)

    values_to_sum = ['ca_labels', 'fr_labels', 'de_labels', 'en_labels', 
    'es_labels', 'it_labels', 'ca_descs', 'fr_descs', 'de_descs', 'en_descs', 
    'es_descs', 'it_descs']

    for value in values_to_sum:
        set_stats_sum_for(values, value)

    env = Environment(loader=FileSystemLoader('./'))
    template = env.get_template('templates/statistics.html')
    r = template.render(values).encode('utf-8')
    return r

@app.route('/render/lletra/<lletra>')
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
