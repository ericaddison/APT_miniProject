import json
import urllib
import urllib2
import os
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler
from source.models.NdbClasses import StreamUser


class CreatePage(BaseHandler):
    def get(self):

        user = StreamUser.get_current_user(self)

        if user:
            login_url = fh.get_logout_url(self, '/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user.nickName,
            'email': user.email,
            'login_url': login_url,
            'login_text': login_text,
            'stream_name_parm': fh.stream_name_parm,
            'tags_parm': fh.tags_parm,
            'cover_url_parm': fh.cover_url_parm,
            'subs_parm': fh.subscribers_parm
            }

        self.set_content_text_html()
        path = os.path.join(os.path.dirname(__file__), '../../templates/Create.html')
        self.response.write(fh.render_html_template(path, template_values))

    def post(self):
        # make call to createStream service
        parm_dict = self.get_request_parameter_dictionary()

        create_stream_url = 'http://{0}/services/createstream?{1}={2};{3}'.format(os.environ['HTTP_HOST'],
                                                                                  fh.user_id_parm,
                                                                                  StreamUser.get_current_user(self).user_id(),
                                                                                  urllib.urlencode(parm_dict))

        try:
            result = urllib2.urlopen(create_stream_url)
            response = json.loads("".join(result.readlines()))
            redirect_url = fh.get_viewstream_url(response[fh.stream_id_parm], 1, 10)
            self.redirect(redirect_url)
        except urllib2.HTTPError:
            self.redirect('/error?{0}={1}'.format(fh.message_parm, 'Error creating stream'))
