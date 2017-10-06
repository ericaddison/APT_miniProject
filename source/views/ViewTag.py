import json
import os
import urllib2

import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler

DEFAULT_IMAGES_PER_PAGE = 10
images_per_page = DEFAULT_IMAGES_PER_PAGE


class ViewTag(BaseHandler):
    def get(self):
        user = fh.get_current_user(self)

        if user:
            login_url = fh.get_logout_url(self, '/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        tag_name = self.get_request_param(fh.tag_name_parm)

        # service call
        tag_service_url = fh.get_tagged_streams_url(tag_name)
        result = urllib2.urlopen(tag_service_url)
        stream_dict = json.loads("".join(result.readlines()))

        stream_ids = stream_dict[fh.stream_id_parm]
        stream_names = stream_dict[fh.stream_name_parm]
        cover_urls = stream_dict[fh.cover_url_parm]
        stream_urls = [fh.get_viewstream_default_url(s) for s in stream_ids]

        streams = []
        for i in range(len(stream_ids)):
            streams.append({'name': stream_names[i],
                            'coverImageURL': cover_urls[i],
                            'url': stream_urls[i]
            })

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user.nickName,
            'email': user.email,
            'login_url': login_url,
            'login_text': login_text,
            'tag_name': tag_name,
            'streams': streams
            }

        self.set_content_text_html()
        path = os.path.join(os.path.dirname(__file__), '../../templates/ViewTag.html')
        self.response.write(fh.render_html_template(path, template_values))
