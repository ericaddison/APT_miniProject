import webapp2

from source.models.NdbClasses import *
from source.services.Service_Utils import *


# Cron jobs for Trending service
# Every 5mins, go through all Stream.viewList timestamps and remove any which are older than 3hours.
# Every 5mins/1hr/1day, go through StreamUsers.trendEmails to get users emails and send out email with top trending Streams.

class CronTrendsService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        user = get_user_param(self, response)
        if user is None:
            return

        # query for all streams owned by user
        stream_query0 = Stream.query()
        stream_query1 = stream_query0.filter(Stream.owner == user.key)
        stream_result = stream_query1.fetch()
        my_streams = [s.key.id() for s in stream_result]

        # query for all streams subscribed to by user
        sub_query0 = StreamSubscriber.query()
        sub_query1 = sub_query0.filter(StreamSubscriber.user == user.key)
        sub_result = sub_query1.fetch()
        sub_streams = [s.key.id() for s in sub_result]


        # write some stream info
        response['owned_streams'] = my_streams
        response['subscribed_streams'] = sub_streams
        self.response.write(json.dumps(response))


app = webapp2.WSGIApplication([
    ('/services/', CronTrendsService)
], debug=True)