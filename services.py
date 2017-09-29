from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
import webapp2
import os
from NdbClasses import *


class UploadFileForm(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/services/upload')

        #TODO: Make the upload form prettier :)
        # should include stream that it is uploading to (come from request?)
        self.response.out.write("""
        <html><body>
        <form action="{0}" method="POST" enctype="multipart/form-data">
          Upload File: <input type="file" name="file"><br>
          <input type="submit" name="submit" value="Submit">
        </form>
        </body></html>""".format(upload_url))


class UploadFileHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:

            upload = self.get_uploads()[0]
            image_url = images.get_serving_url(upload.key())

            #TODO: need to include stream in upload here...
            image = StreamItem(
                owner=ndb.Key('User', users.get_current_user().user_id()),
                blobKey=upload.key(),
                URL=image_url,
                name=upload.filename)
            image.put()

            print("\n\nimage = {}\n\n".format(image))

            self.response.write("<img src=\"{}\">".format(image_url))

        except Exception as e:
            print(e)
            self.error(500)



app = webapp2.WSGIApplication([
    ('/services/uploadform', UploadFileForm),
    ('/services/upload', UploadFileHandler)
], debug=True)