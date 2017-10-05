import json
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import *
from source.Framework.BaseHandler import BaseHandler


# subscribe to a stream
# takes a stream id and a user id. Creates a new StreamSubscription
class SubscribeToStreamService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get stream name
        stream_id = self.get_request_param(fh.stream_id_parm)
        response[fh.stream_id_parm] = stream_id
        if stream_id is None or stream_id == "":
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.stream_id_parm))
            return

        # get the stream
        stream = Stream.get_by_id(stream_id)

        if stream is None:
            fh.bad_request_error(self, response, 'Invalid Stream ID')
            return

        # get current user
        user_id = self.get_request_param(fh.user_id_parm)
        if user_id is None:
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.user_id_parm))
            return

        # get the user
        user = StreamUser.get_by_id(user_id)

        # create new subscription
        sub = StreamSubscriber.create(stream, user)
        if sub is None:
            response['status'] = "Already subscribed"
        else:
            response['status'] = "Subscription created"

        self.write_response(json.dumps(response))


# unsubscribe from a stream
# takes a stream id and a user id. Deletes a StreamSubscription
class UnsubscribeFromStreamService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get stream name
        stream_id = self.get_request_param(fh.stream_id_parm)
        response[fh.stream_id_parm] = stream_id
        if stream_id is None:
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.stream_id_parm))
            return

        # get the stream
        stream = Stream.get_by_id(stream_id)

        # get current user
        user_id = self.get_request_param(fh.user_id_parm)
        if user_id is None:
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.user_id_parm))
            return

        # get the user
        user = StreamUser.get_by_id(user_id)

        # delete subscription
        result = StreamSubscriber.delete(stream, user)
        if result:
            response['status'] = "Subscription deleted"
        else:
            response['status'] = "Subscription not found"

        print("\n{}\n".format(response))

        self.write_response(json.dumps(response))
