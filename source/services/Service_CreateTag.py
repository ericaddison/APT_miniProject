import json

from source.Framework.BaseHandler import BaseHandler
import source.Framework.Framework_Helpers as FH
from source.models.NdbClasses import Tag


# create a Tag
# takes a tag name and attempts to create a new tag. Returns status in json response
class CreateTagService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        tag_name = self.get_request_param(FH.tag_name_parm)
        response[FH.tag_name_parm] = tag_name

        if tag_name is None:
            FH.bad_request_error(self, response, "No tag name found")
            return

        tag = Tag.create(tag_name)
        if not tag:
            FH.bad_request_error(self, response, "Tag {} already exists".format(tag_name))
            return

        # add tag to document index for searching
        FH.searchablize_tag(tag, response)

        response['status'] = "Created new tag: {}".format(tag_name)
        self.write_response(json.dumps(response))
