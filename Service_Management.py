from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
import re
import json
from NdbClasses import *

user_id_parm = 'userID'


# stream management service
# which takes a user id and returns two lists of streams: streams owned and streams subscribed
class ManagementService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        # request parameter error checking
        if user_id_parm not in self.request.GET.keys():
            response['error'] = "No userID found"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        # retrieve request parameters
        user_id = self.request.GET[user_id_parm]
        response[user_id_parm] = user_id

        # retrieve user
        try:
            user = ndb.Key('StreamUser', int(user_id)).get()
        except:
            response['error'] = "Error looking up userID = ".format(user_id)
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        if not user:
            response['error'] = "No user found for userID = {}".format(user_id)
            self.response.set_status(400)
            self.response.write(json.dumps(response))
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