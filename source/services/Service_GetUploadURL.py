import json
from source.Framework.BaseHandler import BaseHandler
from google.appengine.ext import blobstore


class GetUploadURL(BaseHandler):
    def get(self):
        self.set_content_text_json()

        upload_url = blobstore.create_upload_url('/services/upload')

        self.write_response(upload_url)
