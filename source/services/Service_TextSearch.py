import webapp2

from source.models.NdbClasses import *
from source.services.Service_Utils import *
from google.appengine.api import search
from source.services.Service_Utils import get_search_string_param, tag_index_name, search_index_namespace


# search for streams
# takes a text string, returns streams that have the string in the name or tags
# do better ... use the google search API...
class StreamTextSearchService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        search_string = get_search_string_param(self, response)
        if search_string is None:
            return

        index = search.Index(name=tag_index_name, namespace=search_index_namespace)
        results = index.search("string: {}".format(search_string))
        print(results)
        response['tags'] = [str(res.fields[0].value) for res in results.results]
        self.response.set_status(200)
        self.response.write(json.dumps(response))


app = webapp2.WSGIApplication([
    ('/services/search', StreamTextSearchService)
], debug=True)