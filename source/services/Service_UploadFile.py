import json
import urllib2
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
        url = self.get_request_param(fh.url_parm)
        

        if upload is not None:
            image_url = fh.get_file_url(upload)
            name = upload.filename
        elif url not in [None, '']:
            try:
                urllib2.urlopen(url)
                image_url = url
                name = upload
            except:
                image_url = None
        else:
            image_url = None

        if image_url is not None:

            iscover = self.get_request_param('iscover')
            if iscover:
                stream.set_cover_image_url(image_url)
            else:
                
                lat = self.get_request_param('lat')
                print "Latitude = ", lat
                lng = self.get_request_param('lng')
                print "Longitude = ", lng

                # create StreamItem entity
                item = StreamItem.create(
                    owner=user,
                    file=upload,
                    URL=image_url,
                    name=name,
                    stream=stream,
                    latitude=lat,
                    longitude=lng)

                # update stream list of images
                stream.add_item(item)

        # go back to viewstream page
        redirect = str(self.get_request_param(fh.redirect_parm))
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
