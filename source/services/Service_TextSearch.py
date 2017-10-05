import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh


# search for tags
# takes a text string, returns tags that have the string in the name or tags
# do better ... use the google search API...
class TagTextSearchService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        search_string = self.get_request_param(fh.search_string_parm)
        if search_string is None:
            fh.bad_request_error(self, "Search string not found")
            return

        response['tags'] = fh.search_tag_index(search_string)
        self.response.set_status(200)
        self.response.write(json.dumps(response))
