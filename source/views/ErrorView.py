import json
import os

import jinja2
import urllib2
import webapp2

from datetime import datetime

from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import users

import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler


class ErrorView(BaseHandler):
    def get(self):

        error_code = self.get_request_param(fh.error_code)

        # no error error_code in URL
        if error_code == "":
            error_code = -1
            error_string = "No error code given in URL"

        else:
            # get error error_code from URL and convert unicode to integer
            error_code = int(self.get_request_param(fh.error_code))

            # if error error_code in dictionary, look it up.
            if error_code in fh.error_codes:
                error_string = fh.error_codes[error_code]
            else:
                error_string = "Error code {} not in code dictionary".format(error_code)

        template_values = {
            'error_code': error_code,
            'error_string': error_string
        }

        path = os.path.join(os.path.dirname(__file__), '../../templates/ErrorView.html')
        self.set_content_text_html()
        self.write_response(fh.render_html_template(path, template_values))
