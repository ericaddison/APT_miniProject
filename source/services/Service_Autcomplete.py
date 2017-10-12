import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import Stream


class AutocompleteService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        term = self.get_request_param(fh.autocomplete_parm)

        match_streams = fh.search_stream_index_alpha_return_names(term.lower(), 1000)
        match_tags = fh.search_tag_index_alpha(term.lower(), 1000)

        matches = sorted(match_tags+match_streams)[0:20]
        matches.insert(0, len(matches))
        self.write_response(json.dumps(matches))