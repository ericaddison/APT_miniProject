import json
import urllib
import urllib2
import os
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler


class TextSearchForm(BaseHandler):
    def get(self):

        user = fh.get_current_user(self)

        if user:
            login_url = fh.get_logout_url(self, '/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user.nickName,
            'login_url': login_url,
            'login_text': login_text,
            'stream_name_parm': fh.stream_name_parm,
            'tags_parm': fh.tags_parm,
            'cover_url_parm': fh.cover_url_parm,
            'subs_parm': fh.subscribers_parm,
            'search_url': '/searchexe'
            }

        search_string = self.get_request_param(fh.search_string_parm)
        if search_string is not None:
            template_values['search_string'] = search_string

        tags = self.get_request_param(fh.tags_parm)
        if tags not in [None, '']:
            s = urllib.unquote(tags).decode('utf8')
            template_values['search_tags'] = eval(s)

        path = os.path.join(os.path.dirname(__file__), '../../templates/StreamSearch.html')
        self.set_content_text_html()
        self.write_response(fh.render_html_template(path, template_values))


class TextSearch(BaseHandler):
    def post(self):
        response = {}
        search_string = self.get_request_param(fh.search_string_parm)
        if search_string in [None, '']:
            self.redirect('/search')
            return

        # TODO: can we add a range here? like, give me search results 1-10, 11-20, etc?
        # make call to textSearch service
        search_service_url = 'http://{0}/services/searchtags?searchString={1}'.format(os.environ['HTTP_HOST'], urllib.quote(search_string))
        result = urllib2.urlopen(search_service_url)
        search_response = json.loads("".join(result.readlines()))
        print("\n{}\n".format(search_response))
        self.redirect('/search?{}'.format(urllib.urlencode(search_response)))
