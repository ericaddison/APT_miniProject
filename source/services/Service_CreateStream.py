import os
import urllib
import urllib2

import webapp2
from google.appengine.api import users

from source.models.NdbClasses import *
from source.services.Service_Utils import *

# create a stream
class CreateStreamService(webapp2.RequestHandler):
    def post(self):

        user = users.get_current_user()

        streamname = self.request.get('streamname')
        subscribers = self.request.get('subs')
        tags = self.request.get('tags')
        coverImageUrl = self.request.get('coverUrl')
        myStreamUser = ndb.Key('StreamUser', user.user_id()).get()

        subscriberArray = subscribers.split(";")
        tagArray = tags.split(";")

        subUserArray = StreamUser.query(StreamUser.email.IN(subscriberArray)).fetch()
        subUserKeys = [sub.key for sub in subUserArray]

        # create tags (or not if they already exist)
        url_base = 'http://{0}/services/createtag?tagName='.format(os.environ['HTTP_HOST'])
        for tag_name in tagArray:
            tag_service_url = '{0}{1}'.format(url_base, urllib.quote(tag_name))
            resp = urllib2.urlopen(tag_service_url)
            print("\n{}\n".format(resp))

        # Create a new Stream entity then redirect to /view the new stream
        newStreamKey = Stream(name=streamname, owner=myStreamUser.key, coverImageURL=coverImageUrl, numViews=0).put()

        # create new subscriptions for the given users
        for sub in subUserKeys:
            StreamSubscriber(stream=newStreamKey, user=sub).put()

        # associate current tags
        for tag_name in tagArray:
            StreamTag(stream=newStreamKey, tag=ndb.Key('Tag', tag_name)).put()

        # Redirect to /view for this stream
        #self.redirect('/manage')
        self.redirect('/viewstream?streamID={}'.format(newStreamKey.id()))

app = webapp2.WSGIApplication([
    ('/services/createstream', CreateStreamService)
], debug=True)