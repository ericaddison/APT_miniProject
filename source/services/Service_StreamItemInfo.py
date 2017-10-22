import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import StreamItem


#('/services/streamiteminfo', StreamItemInfoService)

#Returns all stream items for all streams
class StreamItemInfoService(BaseHandler):
    def get(self):

        self.set_content_text_json()
        response = []

        all_stream_items = StreamItem.get_all_stream_items()
        for item in all_stream_items:
            dictItem = {"streamid": item.stream.id(),
                        "imageurl": item.URL,
                        "dateadded": item.dateAdded.strftime('%Y-%m-%d %H:%M:%S'),
                        "lat": item.latitude,
                        "lng": item.longitude}
                
            response.append(dictItem)

        print(response)

        self.write_response(json.dumps(response))