import webapp2
import json
import source.Framework.Framework_Helpers as FH
from source.models.NdbClasses import *


# subscribe to a stream
# takes a stream id and a user id. Creates a new StreamSubscription
class SubscribeToStreamService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        # get stream name
        stream_id = FH.get_stream_id_param(self)
        response[FH.stream_id_parm] = stream_id
        if stream_id is None or stream_id == "":
            FH.bad_request_error(self, response, 'No parameter {} found'.format(FH.stream_id_parm))
            return

        # get the stream
        stream = Stream.get_by_id(stream_id)

        if stream is None:
            FH.bad_request_error(self, response, 'Invalid Stream ID')
            return

        # get current user
        user = FH.get_current_user(self)
        if user is None:
            FH.bad_request_error(self, response, 'Not logged in')
            return

        # create new subscription
        sub = StreamSubscriber.create(stream, user)
        if sub is None:
            response['status'] = "Already subscribed"
        else:
            response['status'] = "Subscription created"

        FH.write_response(self, json.dumps(response))


# unsubscribe from a stream
# takes a stream id and a user id. Deletes a StreamSubscription
class UnsubscribeFromStreamService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        # get stream name
        stream_id = FH.get_stream_id_param(self)
        response[FH.stream_id_parm] = stream_id
        if stream_id is None:
            FH.bad_request_error(self, response, 'No parameter {} found'.format(FH.stream_id_parm))
            return

        # get the stream
        stream = Stream.get_by_id(stream_id)

        # get current user
        user = FH.get_current_user(self)
        if user is None:
            FH.bad_request_error(self, response, 'Not logged in')
            return

        # delete subscription
        result = StreamSubscriber.delete(stream, user)
        if result:
            response['status'] = "Subscription deleted"
        else:
            response['status'] = "Subscription not found"

        FH.write_response(self, json.dumps(response))


app = webapp2.WSGIApplication([
    ('/services/subscribe', SubscribeToStreamService),
    ('/services/unsubscribe', UnsubscribeFromStreamService)
], debug=True)