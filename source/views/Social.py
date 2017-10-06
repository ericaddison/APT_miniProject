import os

from google.appengine.api import users

from google.appengine.api import app_identity
from source.models.NdbClasses import *
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler
from google.appengine.ext.webapp import template


class SocialPage(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        # get all users
        all_streams = Stream.query().fetch()

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user,
            'login_url': login_url,
            'login_text': login_text,
            'app': app_identity.get_application_id(),
            'streams': all_streams}

        path = os.path.join(os.path.dirname(__file__), '../../templates/Social.html')
        self.set_content_text_html()
        self.write_response(fh.render_html_template(path, template_values))

