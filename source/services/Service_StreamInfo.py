import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import Stream


# stream info service
# which takes a list of streamIDs
class BatchStreamInfoService(BaseHandler):
    def get(self):

        self.set_content_text_json()
        response = []

        # get stream IDs
        # if none found, return all
        stream_id = self.get_request_param(fh.stream_id_parm)
        if stream_id in ['', None]:
            all_streams = Stream.get_all_streams_by_updated()
            for stream in all_streams:
                response.append(stream.get_meta_dict())
        else:
            ids = json.loads(stream_id)
            try:
                for id in ids:
                    response.append(Stream.get_meta_dict_by_id(id))
            except TypeError:
                response.append(Stream.get_meta_dict_by_id(ids))

        print(response)

        self.write_response(json.dumps(response))
