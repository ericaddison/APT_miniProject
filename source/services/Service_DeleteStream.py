import webapp2

from source.models.NdbClasses import *
from source.services.Service_Utils import *

stream_id_parm = 'streamID'
user_id_parm = 'userID'


# delete a stream
# takes a stream id and a user id. Deletes stream ID and returns status code
class DeleteStreamService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        stream = get_stream_param(self, response)
        if stream is None:
            return

        user = get_user_param(self, response)
        if user is None:
            return

        # check that user is the owner of the stream
        if user.key != stream.owner:
            response['error'] = "Not stream owner"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        # delete the StreamTags associated with this stream
        tags = StreamTag.query(StreamTag.stream == stream.key).fetch()
        for tag in tags:
            tag.key.delete()

        # delete StreamSubscribers associated with this stream
        subs = StreamSubscriber.query(StreamSubscriber.stream == stream.key)
        for sub in subs:
            sub.key.delete()

        # delete the stream itself
        stream.key.delete()

        self.response.set_status(200)
        self.response.write(json.dumps(response))


app = webapp2.WSGIApplication([
    ('/services/deletestream', DeleteStreamService)
], debug=True)