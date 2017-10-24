import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import StreamItem
from source.models.NdbClasses import Stream


#('/services/streamiteminfo', StreamItemInfoService)
# or
#('/services/streamiteminfo?streamid=5629499534213120')

#Returns all stream items for all streams
class StreamItemInfoService(BaseHandler):
    def get(self):

        #If parameter of id=, then return only the items with that streams ID.
        #Otherwise return all items.
        
        self.set_content_text_json()
        response = []
        
        streamid = self.get_request_param("streamid")
        
        if (streamid == None) or (streamid == ''):        
            my_stream_items = StreamItem.get_all_stream_items()

        else:
            my_stream_items = StreamItem.get_stream_items_by_key(long(streamid))
        
        for item in my_stream_items:
            dictItem = {"streamid": item.stream.id(),
                        "streamname": Stream.get_by_id(item.stream.id()).name,
                        "imageurl": item.URL,
                        "dateadded": item.dateAdded.strftime('%Y-%m-%d %H:%M:%S'),
                        "lat": item.latitude,
                        "lng": item.longitude}
                
            response.append(dictItem)
                
        print(response)

        self.write_response(json.dumps(response))