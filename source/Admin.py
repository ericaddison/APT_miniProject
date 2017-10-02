import os

import jinja2
import webapp2
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

from source.models.NdbClasses import *


class AdminDashboard(webapp2.RequestHandler):
    def get(self):

        if not users.IsCurrentUserAdmin():
            self.redirect("/admin/notadmin")

        template = JINJA_ENVIRONMENT.get_template('templates/admin/AdminDashboard.html')
        self.response.write(template.render({}))


class ListUsers(webapp2.RequestHandler):
    def get(self):

        if not users.IsCurrentUserAdmin():
            self.redirect("/admin/notadmin")

        # get all users
        all_users = StreamUser.query().fetch()

        template_values = {
            'users': all_users
        }



        template = JINJA_ENVIRONMENT.get_template('templates/admin/AdminListUsers.html')
        self.response.write(template.render(template_values))


class ListStreams(webapp2.RequestHandler):
    def get(self):

        if not users.IsCurrentUserAdmin():
            self.redirect("/admin/notadmin")

        # get all users
        all_streams = Stream.query().fetch()

        template_values = {
            'streams': all_streams,
            'len': len
        }

        template = JINJA_ENVIRONMENT.get_template('templates/admin/AdminListStreams.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/admin/dashboard', AdminDashboard),
    ('/admin/listusers', ListUsers),
    ('/admin/liststreams', ListStreams)
], debug=True)


