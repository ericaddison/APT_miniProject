import webapp2
import json
from source.services.Service_Utils import get_tag_param, tag_name_parm, searchablize_tag_or_stream, tag_index_name
from source.models.NdbClasses import Tag


# create a Tag
# takes a tag name and attempts to create a new tag. Returns status in json response
class CreateTagService(webapp2.RequestHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        tag = get_tag_param(self, response)

        if response[tag_name_parm] is None:
            return

        self.response.set_status(200)
        if tag is not None:
            response['status'] = "Tag {} already exists".format(tag.name)
            self.response.write(json.dumps(response))
            return

        response.pop('error', None)
        tag = Tag(name=tag.name, id=tag.name)
        tag.put()

        # add tag to document index for searching
        searchablize_tag_or_stream(tag, tag_index_name, response)

        response['status'] = "Created new tag: {}".format(tag.name)
        self.response.clear()
        self.response.write(json.dumps(response))
        return


app = webapp2.WSGIApplication([
    ('/services/createtag', CreateTagService)
], debug=True)