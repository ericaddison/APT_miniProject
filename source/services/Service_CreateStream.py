import json
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler
from source.models.NdbClasses import Stream, StreamSubscriber, StreamTag, StreamUser


# create a Tag
# takes a tag name and attempts to create a new tag. Returns status in json response
class CreateStreamService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get current user
        owner_id = self.get_request_param(fh.user_id_parm)
        owner = StreamUser.get_by_id(owner_id)

        if owner is None:
            fh.bad_request_error(self, response, 'Not logged in')
            return

        # get stream name
        stream_name = self.get_request_param(fh.stream_name_parm)
        response[fh.stream_name_parm] = stream_name
        if stream_name is None or stream_name == "":
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.stream_name_parm))
            return

        # get cover image URL
        cover_url = self.get_request_param(fh.cover_url_parm)
        response[fh.cover_url_parm] = cover_url

        # create new stream
        stream = Stream.create(name=stream_name,
                               owner=owner,
                               cover_url=cover_url
                               )

        if stream is None:
            fh.bad_request_error(self, response, 'Stream {0} already exists for user {1}'.format(stream_name, owner.nickName))
            return

        response[fh.stream_id_parm] = stream.key.id()

        # add stream to document index for searching
        fh.searchablize_stream(stream, response)

        # process subscribers list
        subs = self.get_request_param(fh.subscribers_parm)
        response[fh.subscribers_parm] = subs
        num_added = StreamSubscriber.add_subscribers_by_emails(stream, subs.split(';'))
        response['num_new_subscribers'] = num_added

        # process tags list
        #TODO: tags list in create
        tags = self.get_request_param(fh.tags_parm)
        StreamTag.add_tags_to_stream_by_name(stream, tags.split(';'))
        response[fh.tags_parm] = tags

        response['status'] = "Created new stream: {}".format(stream_name)
        self.write_response(json.dumps(response))
