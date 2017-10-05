import webapp2
from google.appengine.api import search

from source.Framework.Framework_Helpers import *
from source.Framework.Framework_Helpers import get_search_string_param, tag_index_name, search_index_namespace


# search for tags
# takes a text string, returns tags that have the string in the name or tags
# do better ... use the google search API...
class TagTextSearchService(webapp2.RequestHandler):
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
    ('/services/searchtags', TagTextSearchService)
], debug=True)