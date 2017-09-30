from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
import re
import json
from NdbClasses import *

stream_id_parm = 'streamID'
image_range_parm = 'imageRange'


# view a stream
# takes a stream id and an image range and returns a list of URLs to images, and an image range
class ViewStreamService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        # request parameter error checking
        if stream_id_parm not in self.request.GET.keys():
            response['error'] = "No streamID found"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        if image_range_parm not in self.request.GET.keys():
            response['error'] = "No image range found"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        # retrieve request parameters
        stream_id = self.request.GET[stream_id_parm]
        image_range = self.request.GET[image_range_parm]
        response[stream_id_parm] = stream_id

        # verify image range format
        m = re.match("^([\d]+)-([\d]+)$", image_range)
        if m is None:
            response['error'] = "Incorrect image range format. Expected <number>-<number>"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        # retrieve the stream from the ID
        stream = (ndb.Key('Stream', int(stream_id))).get()

        if stream is None:
            response['error'] = "Invalid stream ID"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        # write some stream info
        response['streamName'] = stream.name
        response['streamOwner'] = stream.owner.get().nickName

        # get the indices
        ind1, ind2 = sorted([int(ind) for ind in m.groups()])

        l = len(stream.items)
        ind1 = max(1, min(l, ind1))
        ind2 = max(1, min(l, ind2))

        # query for images
        image_urls = [key.get().URL for key in stream.items[ind1-1:ind2]]

        if len(image_urls) == 0:
            response[image_range_parm] = None
        else:
            response[image_range_parm] = "{}-{}".format(ind1, ind2)

        response['urls'] = image_urls
        self.response.write(json.dumps(response))



app = webapp2.WSGIApplication([
    ('/services/viewstream', ViewStreamService)
], debug=True)