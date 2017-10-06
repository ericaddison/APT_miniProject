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

DEFAULT_IMAGES_PER_PAGE = 10
images_per_page = DEFAULT_IMAGES_PER_PAGE


class ViewStream(BaseHandler):
    def get(self):
        user = fh.get_current_user(self)

        if user:
            login_url = fh.get_logout_url(self, '/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        tag_name = self.get_request_param(fh.tag_name_parm)



        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user.nickName,
            'email': user.email,
            'login_url': login_url,
            'login_text': login_text,
            'stream_name_parm': fh.stream_name_parm,
            'tags_parm': fh.tags_parm,
            'cover_url_parm': fh.cover_url_parm,
            'subs_parm': fh.subscribers_parm
            }

        self.set_content_text_html()
        path = os.path.join(os.path.dirname(__file__), '../../templates/Create.html')
        self.response.write(fh.render_html_template(path, template_values))
