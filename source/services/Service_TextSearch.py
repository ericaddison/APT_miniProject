import webapp2

from source.models.NdbClasses import *
from source.services.Service_Utils import *

search_parm = 'searchString'


# search for streams
# takes a text string, returns streams that have the string in the name or tags
# do better ... use the google search API...
class StreamTextSearchService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        search_string = self.request.get(search_parm)
        response['searchString'] = search_string
        if search_string is None or search_string == "":
            response['error'] = "No search string found"
            self.response.set_status(400)
            self.response.write(json.dumps(response))
            return

        # search all tags
        all_tags = Tag.query().fetch()
        matching_tags = [tag.key.id() for tag in all_tags if search_string.lower() in tag.name.lower()]
        response['tags'] = matching_tags

        # search all streams
        all_streams = Stream.query().fetch()
        matching_streams = [st.key.id() for st in all_streams if search_string.lower() in st.name.lower()]
        response['streams'] = matching_streams

        self.response.set_status(200)
        self.response.write(json.dumps(response))


app = webapp2.WSGIApplication([
    ('/services/search', StreamTextSearchService)
], debug=True)