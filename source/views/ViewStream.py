import json
import os

import jinja2
import urllib2
import webapp2

from datetime import datetime

from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import users

import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler

DEFAULT_IMAGES_PER_PAGE = 10
images_per_page = DEFAULT_IMAGES_PER_PAGE


class ViewStream(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return


        # retrieve request parameters
        stream_id = self.get_request_param(fh.stream_id_parm)

        # retrieve the stream from the ID
        try:
            stream = (ndb.Key('Stream', int(stream_id))).get()
        except:
            self.redirect('/')
            return

        if stream is None:
            self.redirect('/')
            return

        #Increment view counter
        stream.viewList.append(datetime.now())
        stream.numViews = stream.numViews+1
        stream.put()
        
        upload_url = blobstore.create_upload_url('/services/upload')

        # get the current image range
        ind1, ind2, status = fh.get_image_range_param(self)
        if ind1 is None or ind2 is None:
            ind1 = 1
            ind2 = images_per_page

        # make call to viewimage service
        viewstream_service_url = fh.get_viewstream_service_url(stream_id, ind1, ind2)

        result = urllib2.urlopen(viewstream_service_url)
        response = json.loads("".join(result.readlines()))
        image_urls = response['urls']

        print(response)

        # get total number of images and make links
        num_images = response[fh.num_images_parm]

        # get next 10 images link
        next_page_url = None
        if ind2 < num_images:
            next_page_url = fh.get_viewstream_url(stream_id, ind1+images_per_page, ind2+images_per_page)

        # get previous 10 images link
        prev_page_url = None
        if ind1 > 1:
            prev_page_url = fh.get_viewstream_url(stream_id, ind1-images_per_page, ind2-images_per_page)

        template_values = {
                    'html_template': 'MasterTemplate.html',
                    'stream': stream,
                    'stream_id': stream.key.id(),
                    'upload_url': upload_url,
                    'image_urls': image_urls,
                    'user': user,
                    'login_url': login_url,
                    'login_text': login_text
                }

        if next_page_url:
            template_values['next_page_url'] = next_page_url

        if prev_page_url:
            template_values['prev_page_url'] = prev_page_url

        path = os.path.join(os.path.dirname(__file__), '../../templates/ViewStream.html')
        self.response.write(template.render(path, template_values))


app = webapp2.WSGIApplication([
    ('/viewstream', ViewStream)
], debug=True)