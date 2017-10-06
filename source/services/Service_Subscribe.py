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
        if user_id is None or user_id == "":
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

        redirect_url = str(self.get_request_param(fh.redirect_parm))

        if redirect_url in ['', None]:
            self.write_response(json.dumps(response))
        else:
            self.redirect(redirect_url)


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
        if user_id is None or user_id == "":
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

        redirect_url = str(self.get_request_param(fh.redirect_parm))

        if redirect_url in ['', None]:
            self.write_response(json.dumps(response))
        else:
            self.redirect(redirect_url)


# check if a user is subscribed to a stream
# takes a stream id and a user id. Returns true or false
class CheckSubscribedService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get stream name
        stream_id = self.get_request_param(fh.stream_id_parm)
        response[fh.stream_id_parm] = stream_id
        if stream_id is None or stream_id == "":
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.stream_id_parm))
            return

        # get current user
        user_id = self.get_request_param(fh.user_id_parm)
        response[fh.user_id_parm] = user_id
        if user_id is None or user_id == "":
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.user_id_parm))
            return

        # create new subscription
        sub = StreamSubscriber.get_by_stream_id_and_user_id(stream_id, user_id)
        if sub is not None:
            response['status'] = True
        else:
            response['status'] = False

        redirect_url = str(self.get_request_param(fh.redirect_parm))

        if redirect_url in ['', None]:
            self.write_response(json.dumps(response))
        else:
            self.redirect(redirect_url)