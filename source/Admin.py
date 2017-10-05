import os

import webapp2
from google.appengine.api import users
from google.appengine.api import search
from google.appengine.ext.webapp import template

from source.models.NdbClasses import *
import source.Framework.Framework_Helpers as fh

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


class ClearSearchIndexes(webapp2.RequestHandler):
    def get(self):
        """Delete all the docs in the given index."""
        index = search.Index(name=fh.tag_index_name, namespace=fh.search_index_namespace)

        msg = 'Deleted all documents from tag index'
        try:
            while True:
                # until no more documents, get a list of documents,
                # constraining the returned objects to contain only the doc ids,
                # extract the doc ids, and delete the docs.
                document_ids = [document.doc_id for document in index.get_range(ids_only=True)]
                if not document_ids:
                    break
                index.delete(document_ids)
        except search.DeleteError:
            msg = 'Error removing exceptions'

        template_values = {
            'simple_content': msg
        }

        self.response.write(template.render(templatepath, template_values))



app = webapp2.WSGIApplication([
    ('/admin/dashboard', AdminDashboard),
    ('/admin/listusers', ListUsers),
    ('/admin/liststreams', ListStreams),
    ('/admin/cleartagindex', ClearSearchIndexes)
], debug=True)


