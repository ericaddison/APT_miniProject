from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
import re
import json
from NdbClasses import *
from Service_Utils import *


# stream management service
# which takes a user id and returns two lists of streams: streams owned and streams subscribed
class ManagementService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        user = get_user_param(self, response)
        if user is None:
            return

        # query for all streams owned by user
        stream_query0 = Stream.query()
        stream_query1 = stream_query0.filter(Stream.owner == user.key)
        stream_result = stream_query1.fetch()
        my_streams = [s.key.id() for s in stream_result]

        # query for all streams subscribed to by user
        sub_query0 = StreamSubscriber.query()
        sub_query1 = sub_query0.filter(StreamSubscriber.user == user.key)
        sub_result = sub_query1.fetch()
        sub_streams = [s.key.id() for s in sub_result]


        # write some stream info
        response['owned_streams'] = my_streams
        response['subscribed_streams'] = sub_streams
        self.response.write(json.dumps(response))


app = webapp2.WSGIApplication([
    ('/services/management', ManagementService)
], debug=True)