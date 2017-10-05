import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh


# search for tags
# takes a text string, returns tags that have the string in the name or tags
class TagTextSearchService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        search_string = self.get_request_param(fh.search_string_parm)
        if search_string is None:
            fh.bad_request_error(self, "Search string not found")
            return

        response['tags'] = fh.search_tag_index(search_string)
        self.write_response(json.dumps(response))


# search for streams
# takes a text string, returns streams that have the string in the name
class StreamTextSearchService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        search_string = self.get_request_param(fh.search_string_parm)
        if search_string is None:
            fh.bad_request_error(self, "Search string not found")
            return

        results = fh.search_stream_index(search_string)
        response[fh.stream_id_parm] = results
        self.write_response(json.dumps(response))
