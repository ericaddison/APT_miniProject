import json
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import Stream, StreamUser
from source.Framework.BaseHandler import BaseHandler


# delete a stream
# takes a stream id and a user id. Deletes stream ID and returns status code
class DeleteStreamService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get stream name
        stream_id = self.get_request_param(fh.stream_id_parm)
        response[fh.stream_id_parm] = stream_id
        if stream_id is None or stream_id == "":
            fh.bad_request_error(self, response, 'No parameter {} found'.format(FH.stream_id_parm))
            return

        # get the stream
        stream = Stream.get_by_id(stream_id)

        if stream is None:
            fh.bad_request_error(self, response, 'Invalid Stream ID')
            return

        # check that user is the owner of the stream
        user_id = self.get_request_param(fh.user_id_parm)
        if user_id != stream.get_owner_from_db().user_id():
            fh.bad_request_error(self, response, 'Not stream owner')
            return

        # delete the stream
        stream.delete()

        self.write_response(json.dumps(response))
