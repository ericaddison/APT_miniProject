import json
import source.Framework.Framework_Helpers as FH
from source.Framework.BaseHandler import BaseHandler
from source.models.NdbClasses import Stream


# create a Tag
# takes a tag name and attempts to create a new tag. Returns status in json response
class CreateStreamService(BaseHandler):
    def get(self):

        FH.set_content_text_plain(self)
        response = {}

        # get current user
        owner = FH.get_current_user(self)
        if owner is None:
            FH.bad_request_error(self, response, 'Not logged in')
            return

        # get stream name
        stream_name = FH.get_stream_name_param(self)
        response[FH.stream_name_parm] = stream_name
        if stream_name is None or stream_name == "":
            FH.bad_request_error(self, response, 'No parameter {} found'.format(stream_name_parm))
            return

        # get cover image URL
        cover_url = FH.get_cover_url_param(self)
        response[FH.cover_url_parm] = cover_url

        # create new stream
        stream = Stream.create(name=stream_name,
                               owner=owner,
                               cover_url=cover_url
                               )

        if stream is None:
            FH.bad_request_error(self, response, 'Stream {0} already exists for user {1}'.format(stream_name, owner.nickName))
            return

        # add stream to document index for searching
        FH.searchablize_stream(stream, response)

        # process subscribers list
        subs = FH.get_subscribers_param(self)
        response[FH.subscribers_parm] = subs
        num_added = FH.add_subscribers(stream, subs.split(';'))
        response['num_new_subscribers'] = num_added

        # process tags list
        tags = FH.get_tags_param(self)
        response[FH.tags_parm] = tags

        response['status'] = "Created new stream: {}".format(stream_name)
        FH.write_response(self, json.dumps(response))
