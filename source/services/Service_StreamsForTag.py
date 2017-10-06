import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import StreamTag


# get streams for a given tag service
# takes a tag name, returns a list of stream ids
class StreamsForTagService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get current user
        tag_name = self.get_request_param(fh.tag_name_parm)
        if tag_name in ['', None]:
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.tag_name_parm))
            return

        # query for all streams owned by user
        tag_streams = StreamTag.get_batch_by_tag_name(tag_name)

        # write some stream info
        response['streams'] = [s.get_stream_id() for s in tag_streams]
        self.write_response(json.dumps(response))
