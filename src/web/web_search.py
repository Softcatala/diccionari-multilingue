#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2014-2015 Jordi Mas i Hernandez <jmas@softcatala.org>
# Copyright (c) 2014 Leandro Regueiro Iglesias <leandro.regueiro@gmail.com>
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
from jinja2 import Environment, FileSystemLoader
from urlparse import urlparse


sys.path.append('models/')
from pagination import Pagination
from search import Search


class WebView(object):

    def _get_result(self, result, key):
        if key in result:
            return cgi.escape(result[key]) 

        return None

    def get_result(self, result):
        image = self._get_result(result, "image")
        if 'permission' in result:
            permission = result["permission"]
        else:
            permission = None

        result_dict = {
            'word_ca': self._get_result(result, "word_ca"),
            'definition_ca' : self._get_result(result, "definition_ca"),
            'word_en': self._get_result(result, "word_en"),
            'definition_en' : self._get_result(result, "definition_en"),
            'word_fr': self._get_result(result, "word_fr"),
            'definition_fr' : self._get_result(result, "definition_fr"),
            'word_de': self._get_result(result, "word_de"),
            'definition_de' : self._get_result(result, "definition_de"),
            'word_es': self._get_result(result, "word_es"),
            'definition_es' : self._get_result(result, "definition_es"),
            'image' : image,
            'permission' : permission,
            'gec' : self._get_result(result, "gec"),
            'wikidata_id' : self._get_result(result, "wikidata_id"),
            'ca_wikiquote' : self._get_result(result, "ca_wikiquote"),
        }

        return result_dict

    def do(self, search):
        """Search a term in the Whoosh index."""
        aborted_search = False
        results = []
        num_results = 0
        total_time = 0
        PER_PAGE = 100

        if search.has_invalid_search_term:
            aborted_search = True
            pagination = None
        else:
            start_time = time.time()
            raw_results = search.get_results()
            total_time = time.time() - start_time
            num_results = raw_results.scored_length()

            if len(raw_results) > 0:

                url = request.url.encode('utf-8')
                o = urlparse(url)
                url = '?' + o.query

                pagination = Pagination(PER_PAGE, len(raw_results), url)
                start = (pagination.page - 1) * PER_PAGE
                end = start

                max_end = start + PER_PAGE
                if num_results - start < max_end:
                    end += num_results - start
                else:
                    end += PER_PAGE

                for i in xrange(start, end):
                    results.append(self.get_result(raw_results[i]))
            else:
                pagination = None

        ctx = {
            'results': results,
            'num_results': num_results,
            'time': "{:.2f}".format(total_time),
            'aborted_search': aborted_search,
            'pagination': pagination,
        }

        env = Environment(loader=FileSystemLoader('./'))
        template = env.get_template('templates/search_results.html')
        r = template.render(ctx).encode('utf-8')
        return r

class IndexView(object):

    def __init__(self, lletra):
        self.lletra = lletra

    def _get_result(self, result, key):
        if key in result:
            return cgi.escape(result[key]) 

        return None

    def get_result(self, result):
        result_dict = {
            'word_ca': self._get_result(result, "word_ca")
        }

        return result_dict

    def do(self, search):
        """Search a term in the Whoosh index."""
        aborted_search = False
        results = []
        num_results = 0
        total_time = 0
        PER_PAGE = 100

        start_time = time.time()
        raw_results = search.get_results()
        total_time = time.time() - start_time
        num_results = raw_results.scored_length()

        if len(raw_results) > 0:

            url = request.url.encode('utf-8')
            o = urlparse(url)
            url = self.lletra + '?' + o.query

            pagination = Pagination(PER_PAGE, len(raw_results), url)
            pagination.separator = '?'
            start = (pagination.page - 1) * PER_PAGE
            end = start

            max_end = start + PER_PAGE
            if num_results - start < max_end:
                end += num_results - start
            else:
                end += PER_PAGE

            for i in xrange(start, end):
                results.append(self.get_result(raw_results[i]))
        else:
            pagination = None

        ctx = {
            'results': results,
            'num_results': num_results,
            'time': "{:.2f}".format(total_time),
            'lletra': self.lletra,
            'pagination': pagination,
        }

        env = Environment(loader=FileSystemLoader('./'))
        template = env.get_template('templates/index_letter.html')
        r = template.render(ctx).encode('utf-8')
        return r


app = Flask(__name__)


@app.route('/')
def search_request():
    source = request.args.get('source')
    search = Search(source)
    View = WebView()
    result = View.do(search)
    return result

@app.route('/lletra/<lletra>')
def dict_index(lletra):
    start = lletra.find('?')
    if start != -1:
        lletra = lletra[:start]
    
    #return "<p>Hello2 {0}</p>".format(lletra)
    search = Search(lletra)
    search.Index = True
    search.Duplicates = False
    View = IndexView(lletra)
    result = View.do(search)
    return result
    

if __name__ == '__main__':
    app.debug = True
    app.run()
