from google.appengine.ext import blobstore
from google.appengine.ext import ndb
import webapp2
import json
import urllib2
from NdbClasses import Stream

import os
import jinja2
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

stream_id_parm = 'streamID'


class ViewStream(webapp2.RequestHandler):
    def get(self):

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

        template_values = {
                    'stream': stream,
                    'upload_url': upload_url,
                    'image_urls': image_urls
                }

        template = JINJA_ENVIRONMENT.get_template('templates/ViewStream.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/viewstream', ViewStream)
], debug=True)