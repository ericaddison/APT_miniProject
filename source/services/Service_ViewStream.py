import json
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler
from source.models.NdbClasses import Stream, StreamTag


# view a stream
# takes a stream id and an image range and returns a list of URLs to images, and an image range, and tag names
class ViewStreamService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        stream_id = self.get_request_param(fh.stream_id_parm)
        if stream_id is None or stream_id == '':
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.stream_id_parm))
            return

        # get the stream
        stream = Stream.get_by_id(stream_id)

        if stream is None:
            fh.bad_request_error(self, response, 'Invalid Stream ID')
            return

        # write some stream info
        response[fh.stream_name_parm] = stream.name
        response[fh.owner_parm] = stream.get_owner_from_db().nickName
        response[fh.num_images_parm] = len(stream.items)

        # get the indices
        ind1, ind2, status = fh.get_image_range_param(self)
        if ind1 is None or ind2 is None:
            fh.bad_request_error(self, response, status)
            return

        # query for images
        items, in1, ind2 = stream.get_items(ind1, ind2)
        image_urls = [item.URL for item in items]

        if len(image_urls) == 0:
            response[fh.image_range_parm] = None
        else:
            response[fh.image_range_parm] = "{0}-{1}".format(ind1, ind2)

        # get the tags
        stream_tags = StreamTag.get_batch_by_stream(stream)
        response[fh.tags_parm] = [t.get_tag_name() for t in stream_tags]

        response['urls'] = image_urls
        self.write_response(json.dumps(response))
