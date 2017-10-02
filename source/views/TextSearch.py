import json
import os

import jinja2
import urllib2
import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template


class TextSearchForm(webapp2.RequestHandler):
    def get(self):

        self.response.write('Search form!')

        # urlopen here

        # send results to template


#        template_values = {
#                    'stream': stream,
#                    'upload_url': upload_url,
#                    'image_urls': image_urls
#                }

#        path = os.path.join(os.path.dirname(__file__), '../../templates/ViewStream.html')
#        self.response.write(template.render(path, template_values))


app = webapp2.WSGIApplication([
    ('/search', TextSearchForm)
], debug=True)