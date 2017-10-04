import json
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler
from source.models.NdbClasses import Stream


# view a stream
# takes a stream id and an image range and returns a list of URLs to images, and an image range
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
        response['streamName'] = stream.name
        response['streamOwner'] = stream.get_owner_from_db().nickName

        # get the indices
        ind1, ind2, status = fh.get_image_range_param(self)

        if ind1 is None or ind2 is None:
            fh.bad_request_error(self, response, status)
            return

        # query for images
        items = stream.get_items(ind1, ind2)
        image_urls = [item.URL for item in items]

        if len(image_urls) == 0:
            response[fh.image_range_parm] = None
        else:
            response[fh.image_range_parm] = "{0}-{1}".format(ind1, ind2)

        response['urls'] = image_urls
        self.write_response(json.dumps(response))
