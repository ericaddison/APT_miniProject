import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import StreamSubscriber, Stream, StreamUser


# stream management service
# which takes a user id and returns two lists of streams: streams owned and streams subscribed
class ManagementService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

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
