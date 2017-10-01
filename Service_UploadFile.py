from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import json
import webapp2
from NdbClasses import *

stream_id_parm = 'streamID'


# expects a GET parameter 'streamID' containing the stream ID
class UploadFileHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:

            # check valid streamID
            stream_id = self.request.POST[stream_id_parm]
            stream = ndb.Key('Stream', int(stream_id)).get()

            # if stream not found
            if not stream:
                self.redirect("/?error=badStreamID")

            upload = self.get_uploads()[0]
            image_url = images.get_serving_url(upload.key())

            # create StreamItem entity
            image = StreamItem(
                owner=ndb.Key('StreamUser', users.get_current_user().user_id()),
                blobKey=upload.key(),
                URL=image_url,
                name=upload.filename,
                stream=stream.key)
            image.put()

            # update stream list of images
            stream.items.append(image.key)
            stream.put()

            # go back to viewstream page
            self.redirect("/viewstream?streamID={}".format(stream_id))

        except Exception as e:
            print(e)
            self.error(500)


app = webapp2.WSGIApplication([
    ('/services/upload', UploadFileHandler)
], debug=True)