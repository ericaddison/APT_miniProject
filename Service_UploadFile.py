from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
import json
import webapp2
from NdbClasses import *
from Service_Utils import *


# expects a POST parameter 'streamID' containing the stream ID
# if a 'redirect' POST parameter is provided, this service will redirect to the give URL
# otherwise a JSON status message will be returned
class UploadFileHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:

            stream = get_stream_param(self, {})
            if stream is None:
                return

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
            redirect = self.request.get('redirect')
            if redirect:
                self.redirect(redirect)
                return
            else:
                self.response.content_type = 'text/plain'
                response = {'status': 'Upload successful'}
                self.response.write(json.dumps(response))
                return

        except Exception as e:
            print(e)
            self.error(500)


app = webapp2.WSGIApplication([
    ('/services/upload', UploadFileHandler)
], debug=True)