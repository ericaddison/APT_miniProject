import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import Stream


class AutocompleteService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        term = self.get_request_param(fh.autocomplete_parm)

        match_streams = fh.search_stream_index(term.lower())
        stream_names = [s.name for s in Stream.get_batch_by_ids(match_streams)]

        match_tags = fh.search_tag_index(term.lower())

        self.write_response(json.dumps(stream_names+match_tags))