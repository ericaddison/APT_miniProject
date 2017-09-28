from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2

import os
import jinja2
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

from NdbClasses import *
import os

class ListUsers(webapp2.RequestHandler):
    def get(self):

        if not users.IsCurrentUserAdmin():
            self.redirect("/admin/notadmin")

        # get all users
        all_users = StreamUser.query().fetch()

        template_values = {
            'users': all_users
        }

        template = JINJA_ENVIRONMENT.get_template('templates/ListUsers.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/admin/listusers', ListUsers)
], debug=True)


