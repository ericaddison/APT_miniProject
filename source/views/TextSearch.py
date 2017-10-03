import json
import os

import urllib2
import urllib
import webapp2
from google.appengine.ext.webapp import template
from source.services.Service_Utils import get_search_string_param, get_tags_param


class TextSearchForm(webapp2.RequestHandler):
    def get(self):
        template_values = {'search_url': '/searchexe'}

        search_string = get_search_string_param(self, {})
        if search_string is not None:
            template_values['search_string'] = search_string

        tags = get_tags_param(self, {})
        if tags is not None and tags != "":
            s = urllib.unquote(tags).decode('utf8')
            template_values['search_tags'] = eval(s)

        path = os.path.join(os.path.dirname(__file__), '../../templates/StreamSearch.html')
        self.response.write(template.render(path, template_values))


class TextSearch(webapp2.RequestHandler):
    def post(self):
        self.response.content_type = 'text/plain'
        response = {}

        search_string = get_search_string_param(self, response)
        if search_string is None:
            self.redirect('/')
            return

        # TODO: can we add a range here? like, give me search results 1-10, 11-20, etc?
        # make call to textSearch service
        search_service_url = 'http://{0}/services/search?searchString={1}'.format(os.environ['HTTP_HOST'], urllib.quote(search_string))
        result = urllib2.urlopen(search_service_url)
        search_response = json.loads("".join(result.readlines()))
        self.redirect('/search?{}'.format(urllib.urlencode(search_response)))


app = webapp2.WSGIApplication([
    ('/search', TextSearchForm),
    ('/searchexe', TextSearch)
], debug=True)