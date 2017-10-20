import os

import webapp2
from google.appengine.api import users
from google.appengine.api import search
from google.appengine.ext.webapp import template
import source.models.NdbClasses as models
from google.appengine.ext import ndb

from source.models.NdbClasses import *
import source.Framework.Framework_Helpers as fh

templatepath = os.path.join(os.path.dirname(__file__), '../templates/admin/AdminTemplate.html')


class AdminDashboard(webapp2.RequestHandler):
    def get(self):

        if not users.IsCurrentUserAdmin():
            self.redirect("/admin/notadmin")

        template_values = {
            'templatepath': templatepath,
            'dash_active': True
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
            'templatepath': templatepath,
            'listusers_active': True
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
            'templatepath': templatepath,
            'liststreams_active': True
        }

        path = os.path.join(os.path.dirname(__file__), '../templates/admin/AdminListStreams.html')
        self.response.write(template.render(path, template_values))


class ClearSearchIndexes(webapp2.RequestHandler):
    def get(self):
        """Delete all the docs in the given index."""
        tagindex = fh.get_tag_index()
        streamindex = fh.get_stream_index()
        msg = 'Deleted all documents from indexes'
        for index in [tagindex, streamindex]:
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
            'simple_content': msg,
            'cleartagindex_active': True
        }

        self.response.write(template.render(templatepath, template_values))


class DisplayTagIndex(webapp2.RequestHandler):
    def get(self):
        index = fh.get_tag_index()

        res = index.get_range(limit=1000)
        prints = "<h2>Tag index name: {}</h2>".format(fh.get_tag_index_name())
        prints += "<table>"
        prints += "".join(['<tr><td>{0}</td><td>--</td><td>{1}</td></tr>'.format(r.fields[1].value, r.fields[2].value) for r in res.results])
        prints += "</table>"

        template_values = {
            'simple_content': prints,
            'showtagindex_active': True
        }

        self.response.write(template.render(templatepath, template_values))


class DisplayStreamIndex(webapp2.RequestHandler):
    def get(self):
        index = fh.get_stream_index()

        res = index.get_range(limit=1000)
        prints = "<h2>Stream index name: {}</h2>".format(fh.get_stream_index_name())
        prints += "<table>"
        prints += "".join(['{}<br><br>'.format(r.fields) for r in res.results])
        prints += "</table>"

        template_values = {
            'simple_content': prints,
            'showstreamindex_active': True
        }

        self.response.write(template.render(templatepath, template_values))


class RedateStreamNDB(webapp2.RequestHandler):
    def update_schema_task(self):

        # Force ndb to use v2 of the model by re-loading it.
        reload(models)

        # Get all of the entities for this Model.
        query = models.Stream.query()
        streams = query.fetch()

        to_put = []
        for stream in streams:
            if len(stream.items) == 0:
                updated = stream.dateAdded
            else:
                updated = stream.items[0].get().dateAdded

            stream.dateUpdated = updated
            to_put.append(stream)

        # Save the updated entities.
        if to_put:
            ndb.put_multi(to_put)
            return 'Put {} stream entities to Datastore'.format(len(to_put))

    def get(self):
        msg = self.update_schema_task()
        template_values = {
            'simple_content': msg,
            'rebuildStreamNDB_active': True
        }

        self.response.write(template.render(templatepath, template_values))



app = webapp2.WSGIApplication([
    ('/admin/dashboard', AdminDashboard),
    ('/admin/listusers', ListUsers),
    ('/admin/liststreams', ListStreams),
    ('/admin/cleartagindex', ClearSearchIndexes),
    ('/admin/displaytagindex', DisplayTagIndex),
    ('/admin/displaystreamindex', DisplayStreamIndex),
    ('/admin/redatestreamndb', RedateStreamNDB)
], debug=True)


