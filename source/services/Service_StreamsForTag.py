import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import StreamTag, Stream


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
        streamtags = StreamTag.get_batch_by_tag_name(tag_name)
        stream_ids = [st.get_stream_id() for st in streamtags]
        streams = Stream.get_batch_by_ids(stream_ids)

        # write some stream info
        response[fh.stream_id_parm] = [id for id in stream_ids]
        response[fh.cover_url_parm] = [s.coverImageURL for s in streams]
        response[fh.stream_name_parm] = [s.name for s in streams]
        self.write_response(json.dumps(response))
