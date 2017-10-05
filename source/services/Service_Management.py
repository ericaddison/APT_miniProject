import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import StreamSubscriber, Stream


# stream management service
# which takes a user id and returns two lists of streams: streams owned and streams subscribed
class ManagementService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        user = fh.get_current_user(self)
        if user is None:
            fh.bad_request_error(self, "Not logged in")
            return

        # query for all streams owned by user
        my_streams = Stream.get_by_owner(user)

        # query for all streams subscribed to by user
        sub_streams = StreamSubscriber.get_by_user(user)

        # write some stream info
        response['owned_streams'] = my_streams
        response['subscribed_streams'] = sub_streams
        self.write_response(json.dumps(response))
