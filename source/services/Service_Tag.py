import json
import time
import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import StreamTag, Stream, Tag
from source.Framework.BaseHandler import BaseHandler


# add a tag to a stream
# takes a stream id and a tag name. Creates a new StreamTag
class AddTagToStreamService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get stream name
        stream_id = self.get_request_param(fh.stream_id_parm)
        response[fh.stream_id_parm] = stream_id
        if stream_id is None or stream_id == "":
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.stream_id_parm))
            return

        # get the stream
        stream = Stream.get_by_id(stream_id)

        if stream is None:
            fh.bad_request_error(self, response, 'Invalid Stream ID')
            return

        # get tag name
        tag_name = self.get_request_param(fh.tag_name_parm)
        if tag_name is None or tag_name == "":
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.tag_name_parm))
            return

        # get the tag
        tag = Tag.get_or_create_by_name(tag_name)

        # create new streamtag
        StreamTag.add_tags_to_stream_by_name(stream, [tag.name])

        # block until new tag is found
        time.sleep(0.01)
        while StreamTag.get_by_stream_and_tag(stream, tag) is None:
            time.sleep(0.01)

        redirect_url = str(self.get_request_param(fh.redirect_parm))

        if redirect_url in ['', None]:
            self.write_response(json.dumps(response))
        else:
            self.redirect(redirect_url)


# remove a tag from a stream
# takes a stream id and a tag name. Deletes a StreamTag
class RemoveTagFromStreamService(BaseHandler):
    def get(self):

        self.set_content_text_plain()
        response = {}

        # get stream name
        stream_id = self.get_request_param(fh.stream_id_parm)
        response[fh.stream_id_parm] = stream_id
        if stream_id in [None, '']:
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.stream_id_parm))
            return

        # get the stream
        stream = Stream.get_by_id(stream_id)

        if stream is None:
            fh.bad_request_error(self, response, 'Invalid Stream ID')
            return

        # get tag name
        tag_name = self.get_request_param(fh.tag_name_parm)
        if tag_name in [None, '']:
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.tag_name_parm))
            return

        # check how many streams have this tag
        st = StreamTag.get_batch_by_tag_name(tag_name)
        n_streams = len(st)

        # get the tag
        tag = Tag.get_by_name(tag_name)
        if tag is not None:
            # remove streamtags
            StreamTag.delete_tag_from_stream(stream, tag)

            # block until new tag is found
            time.sleep(0.01)
            while StreamTag.get_by_stream_and_tag(stream, tag) is not None:
                time.sleep(0.01)

            if n_streams == 1:
                fh.remove_tag_from_search_index(tag_name, {})
                tag.delete()

        redirect_url = str(self.get_request_param(fh.redirect_parm))

        if redirect_url in ['', None]:
            self.write_response(json.dumps(response))
        else:
            self.redirect(redirect_url)