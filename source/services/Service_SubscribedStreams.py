import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import StreamSubscriber, Stream, StreamUser

import urllib2
import urllib


class SubscribedStreamsService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get auth token, if present
        auth_token = urllib.quote(str(self.get_request_param(fh.auth_token_parm)))
        user_data_str = urllib2.urlopen('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token='+auth_token).read()
        user_data = json.loads(user_data_str)

        # get user from auth token
        user = StreamUser.get_by_email(user_data['email'])

        if user is None:
            fh.bad_request_error(self, response, 'Invalid user')
            return

        # query for all streams subscribed to by user
        sub_streams = StreamSubscriber.get_by_user(user)

        # write some stream info
        response = [s.stream.get().get_meta_dict_with_most_recent_image_url() for s in sub_streams]

        self.write_response(json.dumps(response))
