from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
import re
import json
from NdbClasses import *

stream_id_parm = 'streamID'
user_id_parm = 'userID'


# delete a stream
# takes a stream id and a user id. Deletes stream ID and returns status code
class DeleteStreamService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        # request parameter error checking
        if stream_id_parm not in self.request.GET.keys():
            response['error'] = "No streamID found"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        if user_id_parm not in self.request.GET.keys():
            response['error'] = "No userID found"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        # retrieve request parameters
        stream_id = self.request.GET[stream_id_parm]
        user_id = self.request.GET[user_id_parm]
        response[stream_id_parm] = stream_id
        response[user_id_parm] = user_id

        # retrieve the stream from the ID
        stream = (ndb.Key('Stream', int(stream_id))).get()

        if stream is None:
            response['error'] = "Invalid stream ID"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        # retrieve the user from the ID
        user = (ndb.Key('StreamUser', user_id)).get()

        if user is None:
            response['error'] = "Invalid user ID"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        # check that user is the owner of the stream
        if user.key != stream.owner:
            response['error'] = "Not stream owner"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        # delete the StreamTags associated with this stream
        tags = StreamTag.query(StreamTag.stream == stream.key).fetch()
        for tag in tags:
            tag.key.delete()

        # delete StreamSubscribers associated with this stream
        subs = StreamSubscriber.query(StreamSubscriber.stream == stream.key)
        for sub in subs:
            sub.key.delete()

        # delete the stream itself
        stream.key.delete()

        self.response.set_status(200)
        self.response.write(json.dumps(response))


app = webapp2.WSGIApplication([
    ('/services/deletestream', DeleteStreamService)
], debug=True)