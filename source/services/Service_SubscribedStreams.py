import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import StreamSubscriber, Stream, StreamUser

from google.oauth2 import id_token
from google.auth.transport import requests

CLIENT_ID = "567910868038-rj3rdk31k9mbcf4ftder0rhfqr1vrld4.apps.googleusercontent.com"


class SubscribedStreamsService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get auth token, if present
        auth_token = self.get_request_param(fh.auth_token_parm)

        print("I got auth token " + auth_token)

        try:
            idinfo = id_token.verify_oauth2_token(auth_token, requests.Request(), CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            userid = idinfo['sub']
        except ValueError:
            # Invalid token
            print('BALUEAEORJ!!!')
            pass

        print('\n\nemail={}\n\n'.format(idinfo))


        # get current user
        user_id = self.get_request_param(fh.user_id_parm)
        if user_id in ['', None]:
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.user_id_parm))
            return

        user = StreamUser.get_by_id(user_id)
        if user is None:
            fh.bad_request_error(self, response, 'Invalid user')
            return

        # query for all streams owned by user
        my_streams = Stream.get_ids_by_owner(user)

        # query for all streams subscribed to by user
        sub_streams = StreamSubscriber.get_by_user(user)

        # write some stream info
        response['owned_streams'] = [s for s in my_streams]
        response['subscribed_streams'] = [s.stream.id() for s in sub_streams]
        self.write_response(json.dumps(response))
