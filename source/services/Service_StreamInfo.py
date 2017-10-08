import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import Stream


# stream info service
# which takes a list of streamIDs
class BatchStreamInfoService(BaseHandler):
    def get(self):

        self.set_content_text_json()

        # get current user
        stream_id = self.get_request_param(fh.stream_id_parm)
        if stream_id in ['', None]:
            fh.bad_request_error(self, {}, 'No parameter {} found'.format(fh.stream_id_parm))
            return

        ids = json.loads(stream_id)

        response = []
        try:
            for id in ids:
                response.append(Stream.get_meta_dict_by_id(id))
        except TypeError:
            response.append(Stream.get_meta_dict_by_id(ids))

        print(response)

        self.write_response(json.dumps(response))
