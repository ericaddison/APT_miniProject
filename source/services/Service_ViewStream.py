import webapp2

from source.services.Service_Utils import *


# view a stream
# takes a stream id and an image range and returns a list of URLs to images, and an image range
class ViewStreamService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        stream = get_stream_param(self, response)
        if stream is None:
            return

        # write some stream info
        response['streamName'] = stream.name
        response['streamOwner'] = stream.owner.get().nickName

        # get the indices
        ind1, ind2 = get_image_range_param(self, response)

        if ind1 is None or ind2 is None:
            return

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