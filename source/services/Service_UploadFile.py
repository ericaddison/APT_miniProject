import json
from source.Framework.BaseHandler import FileUploadHandler

import source.Framework.Framework_Helpers as fh
from source.models.NdbClasses import Stream, StreamItem


# expects a POST parameter 'streamID' containing the stream ID
# if a 'redirect' POST parameter is provided, this service will redirect to the give URL
# otherwise a JSON status message will be returned
class UploadFileHandler(FileUploadHandler):
    def post(self):
        response = {}

        # get current user
        user = fh.get_current_user(self)
        if user is None:
            fh.bad_request_error(self, response, 'Not logged in')
            return

        stream_id = self.get_request_param(fh.stream_id_parm)
        if stream_id is None or stream_id == '':
            fh.bad_request_error(self, response, 'No parameter {} found'.format(fh.stream_id_parm))
            return

        # get the stream
        stream = Stream.get_by_id(stream_id)

        if stream is None:
            fh.bad_request_error(self, response, 'Invalid Stream ID')
            return

        upload = fh.get_upload_from_filehandler(self, 0)

        if upload is not None:
            image_url = fh.get_file_url(upload)

            # create StreamItem entity
            item = StreamItem.create(
                owner=user,
                file=upload,
                URL=image_url,
                name=upload.filename,
                stream=stream)

            # update stream list of images
            stream.add_item(item)

        # go back to viewstream page
        redirect = self.get_request_param(fh.redirect_parm)
        if redirect:
            self.redirect(redirect)
            return
        else:
            self.set_content_text_plain()
            response = {'status': 'Upload successful',
                        'image_url': image_url
                        }
            self.write_response(json.dumps(response))
            return
