import json
import re
import urllib2
import os
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler
from source.models.NdbClasses import Stream


class DeletePage(BaseHandler):
    def post(self):

        user = fh.get_current_user(self)

        if user:
            login_url = fh.get_logout_url(self, '/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        stream_ids = json.loads(self.get_request_param(fh.stream_id_parm))
        stream_names = json.loads(self.get_request_param(fh.stream_name_parm))

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user.nickName,
            'login_url': login_url,
            'login_text': login_text,
            'del_streams': zip(stream_ids, stream_names),
            'stream_id_parm': fh.stream_id_parm
            }

        self.set_content_text_html()
        path = os.path.join(os.path.dirname(__file__), '../../templates/Delete.html')
        self.response.write(fh.render_html_template(path, template_values))


class DeleteExe(BaseHandler):
    def post(self):
        user = fh.get_current_user(self)

        if user is None:
            self.redirect("/")
            return

        # make call to deleteStream service

        button = self.get_request_param('button')
        if button == "Cancel":
            self.redirect('/manage?{0}=Delete cancelled'.format(fh.message_parm))
            return

        reg = re.compile(r'^delete_(.*)')

        matches = [reg.match(key) for key in self.get_request_parameter_dictionary().keys()]
        stream_ids = [str(match.groups()[0]) for match in matches if match is not None]

        message = ""
        for id in stream_ids:
            delete_stream_url = 'http://{0}/services/deletestream?{1}={2};{3}={4}'.format(os.environ['HTTP_HOST'],
                                                                                          fh.stream_id_parm,
                                                                                          id,
                                                                                          fh.user_id_parm,
                                                                                          fh.get_current_user(self).user_id())
            try:
                result = urllib2.urlopen(delete_stream_url)
                message = "{0}, {1}".format(message, result)
            except urllib2.HTTPError:
                self.redirect('/error?{0}={1}'.format(fh.message_parm, 'Error deleting stream'))

        # try to wait until streams are really gone...
        for id in stream_ids:
            while Stream.get_by_id(id):
                pass

        self.redirect('http://{0}/manage?{1}={2}'.format(os.environ['HTTP_HOST'], fh.message_parm, 'Deleted streams'))

