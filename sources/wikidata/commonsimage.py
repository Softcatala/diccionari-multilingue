#!/usr/bin/env python
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

import os
import sys
import urllib
import urllib2


from xml.etree import ElementTree
from imagesql import * 

class CommonsImage(object):

    images = 0
    Init = False

    def __init__(self, image):
        self.image = image

        if CommonsImage.Init is False:
            Image.create_table(fail_silently=True)
            CommonsImage.Init = True

    def download(self):
        url = ''
        try:
            image = urllib.quote(self.image)
            url = 'http://tools.wmflabs.org/magnus-toolserver/commonsapi.php?image={0}&thumbwidth=250&thumbheight=250&versions&meta'.format(image)
            return urllib2.urlopen(url).read()
        except Exception as e:
            print("Error downloading {0} - {1}".format(url, e))
            return None

    def get_file(self, url, filename):
        infile = urllib2.urlopen(url)
        output = open(filename, 'wb')
        output.write(infile.read())
        output.close()

    def get_url(self):
        #if CommonsImage.images > 100:
        #    return None
        
        try:
            image = Image.select().where(Image.name==self.image).get()
  
        except Exception as e:
            image = None
    
        if image is not None:
            print "Exists {0}".format(image.url)
            return image.url

        result = self.download()

        if result is None:
            return None

        try:
            xml = ElementTree.fromstring(result)
            image = xml.findtext(".//file//urls//thumbnail")
            if image is None:
                return None
            
            self.get_file(image, "images/" + self.image)
            CommonsImage.images = CommonsImage.images + 1
            
            url = "images/" + urllib.quote(self.image)
            saved_image = Image(name = self.image, 
                                url = url)

            saved_image.save()
            print "saved {0}".format(self.image)
            return self.image

        except Exception as e:
            print("Cannot parse result for {0}".format(self.image))
            return None
