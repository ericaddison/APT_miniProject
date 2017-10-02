import os

import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp import template

from source.models.NdbClasses import *

templatepath = os.path.join(os.path.dirname(__file__), '../templates/admin/AdminTemplate.html')

class AdminDashboard(webapp2.RequestHandler):
    def get(self):

        if not users.IsCurrentUserAdmin():
            self.redirect("/admin/notadmin")

        template_values = {
            'templatepath': templatepath
        }

        path = os.path.join(os.path.dirname(__file__), '../templates/admin/AdminDashboard.html')
        self.response.write(template.render(path, template_values))




class ListUsers(webapp2.RequestHandler):
    def get(self):

        if not users.IsCurrentUserAdmin():
            self.redirect("/admin/notadmin")

        # get all users
        all_users = StreamUser.query().fetch()

        template_values = {
            'users': all_users,
            'templatepath': templatepath
        }

        path = os.path.join(os.path.dirname(__file__), '../templates/admin/AdminListUsers.html')
        self.response.write(template.render(path, template_values))

class ListStreams(webapp2.RequestHandler):
    def get(self):

        if not users.IsCurrentUserAdmin():
            self.redirect("/admin/notadmin")

        # get all users
        all_streams = Stream.query().fetch()

        template_values = {
            'streams': all_streams,
            'templatepath': templatepath
        }

        path = os.path.join(os.path.dirname(__file__), '../templates/admin/AdminListStreams.html')
        self.response.write(template.render(path, template_values))


app = webapp2.WSGIApplication([
    ('/admin/dashboard', AdminDashboard),
    ('/admin/listusers', ListUsers),
    ('/admin/liststreams', ListStreams)
], debug=True)


