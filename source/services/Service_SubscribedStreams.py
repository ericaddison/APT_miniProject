import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import StreamSubscriber, Stream, StreamUser
from oauth2client import client
import httplib2

CLIENT_SECRET_FILE = "./client_secret_567910868038-cmb1ces0165uuhd7crp4ibfub2efj14t.apps.googleusercontent.com.json"


class SubscribedStreamsService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get auth token, if present
        auth_code = self.get_request_param(fh.auth_token_parm)

        print("I got auth token " + auth_code)

        credentials = client.credentials_from_clientsecrets_and_code(
            CLIENT_SECRET_FILE,
            ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
            auth_code)

        # Call Google API
        http_auth = credentials.authorize(httplib2.Http())

        # Get profile info from ID token
        userid = credentials.id_token['sub']
        email = credentials.id_token['email']


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
