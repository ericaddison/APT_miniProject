import json

from source.Framework.BaseHandler import BaseHandler
from source.Framework.Framework_Helpers import bad_request_error, write_response
from source.Framework.Framework_Helpers import get_tag_name_param, tag_name_parm, searchablize_tag
from source.models.NdbClasses import Tag


# create a Tag
# takes a tag name and attempts to create a new tag. Returns status in json response
class CreateTagService(BaseHandler):
    def get(self):

        self.response.content_type = 'text/plain'
        response = {}

        tag_name = get_tag_name_param(self)
        response[tag_name_parm] = tag_name

        if tag_name is None:
            bad_request_error(self, response, "No tag name found")
            return

        tag = Tag.create(tag_name)
        if not tag:
            bad_request_error(self, response, "Tag {} already exists".format(tag_name))
            return

        # add tag to document index for searching
        searchablize_tag(tag, response)

        response['status'] = "Created new tag: {}".format(tag_name)
        write_response(self, json.dumps(response))
