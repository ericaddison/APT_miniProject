import webapp2
import json
import datetime
from google.appengine.api import search
from source.services.Service_Utils import get_tag_param, tag_name_parm
from source.models.NdbClasses import Tag

search_index_namespace = 'connexion'
tag_index_name = 'tag_index'


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
        tag = Tag(name=response[tag_name_parm],
                  id=response[tag_name_parm]
                  )

        tag.put()

        # add tag to document index
        index = search.Index(name=tag_index_name, namespace=search_index_namespace)
        doc = search.Document(fields=[search.TextField(name='name', value=tag.name),
                                      search.DateField(name='date_added',
                                                       value=datetime.datetime.now().date())])

        # Index the document.
        try:
            res = index.put(doc)
        except search.PutError, e:
            result = e.results[0]
            response['errResult'] = str(result)

        response['status'] = "Created new tag: {}".format(tag.name)
        self.response.clear()
        self.response.write(json.dumps(response))
        return


app = webapp2.WSGIApplication([
    ('/services/createtag', CreateTagService)
], debug=True)