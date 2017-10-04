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

stream_id_parm = 'streamID'


class ViewStream(webapp2.RequestHandler):
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
        stream_id = self.request.GET[stream_id_parm]

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


        print("\n\n\n{}\n\n\n".format(os.environ['HTTP_HOST']))


        #TODO: See if there is some way to use a relative URL here, or to automatically get the first part...
        # got this with HTTP_HOST
        # now how to get protocol? http vs https?


        # make call to viewimage service
        viewstream_service_url = 'http://{0}/services/viewstream?streamID={1};imageRange={2}'.format(os.environ['HTTP_HOST'],stream_id, '1-10')
        result = urllib2.urlopen(viewstream_service_url)
        response = json.loads("".join(result.readlines()))
        image_urls = [str(url) for url in response['urls']]
        image_urls.reverse()

        template_values = {
                    'html_template': 'MasterTemplate.html',
                    'stream': stream,
                    'upload_url': upload_url,
                    'image_urls': image_urls,
                    'user': user,
                    'login_url': login_url,
                    'login_text': login_text
                }

        path = os.path.join(os.path.dirname(__file__), '../../templates/ViewStream.html')
        self.response.write(template.render(path, template_values))


app = webapp2.WSGIApplication([
    ('/viewstream', ViewStream)
], debug=True)