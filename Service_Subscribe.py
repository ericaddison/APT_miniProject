from google.appengine.ext import ndb
import webapp2
import json
from NdbClasses import *
from Service_Utils import *


# subscribe to a stream
# takes a stream id and a user id. Creates a new StreamSubscription
class SubscribeToStreamService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        stream = get_stream_param(self, response)
        if stream is None:
            return

        user = get_user_param(self, response)
        if user is None:
            return

        # create new subscription
        key_value = "{}-{}".format(user.key.id(), stream.key.id())
        sub = ndb.Key('StreamSubscriber', key_value).get()
        print("\n\n\n{}\n\n".format(sub))
        if sub is None:
            StreamSubscriber(user=user.key,
                             stream=stream.key,
                             id=key_value).put()
            response['status'] = "Subscription created"
        else:
            response['status'] = "Already subscribed"

        self.response.set_status(200)
        self.response.write(json.dumps(response))


# unsubscribe from a stream
# takes a stream id and a user id. Deletes a StreamSubscription
class UnsubscribeFromStreamService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        stream = get_stream_param(self, response)
        if stream is None:
            return

        user = get_user_param(self, response)
        if user is None:
            return

        # delete subscription
        key_value = "{}-{}".format(user.key.id(), stream.key.id())
        sub = ndb.Key('StreamSubscriber', key_value).get()
        if sub is None:
            response['status'] = "Subscription not found"
        else:
            sub.key.delete()
            response['status'] = "Subscription deleted"

        self.response.set_status(200)
        self.response.write(json.dumps(response))


app = webapp2.WSGIApplication([
    ('/services/subscribe', SubscribeToStreamService),
    ('/services/unsubscribe', UnsubscribeFromStreamService)
], debug=True)