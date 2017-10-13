import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import Stream


class AutocompleteService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        term = self.get_request_param(fh.autocomplete_parm)

        match_streams = fh.search_stream_index_alpha_return_names(term.lower(), 100)
        match_tags = fh.search_tag_index_alpha(term.lower(), 100)

        matches = sorted(match_tags+match_streams, key=search_key)[0:20]
        self.write_response(json.dumps(matches))


def search_key(s):
    return str(s).lower()
