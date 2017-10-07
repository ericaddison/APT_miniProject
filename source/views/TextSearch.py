import json
import urllib
import urllib2
import os
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler
from source.models.NdbClasses import Stream


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
            tags = eval(s)
            template_values['search_tags'] = [{'name': tag, 'url': fh.get_viewtag_url(tag)} for tag in tags]

        stream_ids = self.get_request_param(fh.stream_id_parm)
        if stream_ids not in [None, '']:
            s = urllib.unquote(stream_ids).decode('utf8')
            ids = eval(s)
            template_values['search_streams'] = Stream.get_batch_by_ids(ids)

        path = os.path.join(os.path.dirname(__file__), '../../templates/StreamSearch.html')
        self.set_content_text_html()
        self.write_response(fh.render_html_template(path, template_values))


class TextSearch(BaseHandler):
    def post(self):
        response = {}
        search_string = self.get_request_param(fh.search_string_parm).strip()
        if search_string in [None, '']:
            self.redirect('/search')
            return

        # TODO: can we add a range here? like, give me search results 1-10, 11-20, etc?
        # make call to textSearch service
        search_service_url = 'http://{0}/services/searchtags?searchString={1}'.format(os.environ['HTTP_HOST'], urllib.quote(search_string))
        result = urllib2.urlopen(search_service_url)
        tag_search = json.loads("".join(result.readlines()))

        search_service_url = 'http://{0}/services/searchstreams?searchString={1}'.format(os.environ['HTTP_HOST'],
                                                                                      urllib.quote(search_string))
        result = urllib2.urlopen(search_service_url)
        stream_search = json.loads("".join(result.readlines()))

        response = {
                    fh.search_string_parm: search_string,
                    fh.tags_parm: tag_search[fh.tags_parm],
                    fh.stream_id_parm: stream_search[fh.stream_id_parm]
                    }

        self.redirect('/search?{}'.format(urllib.urlencode(response)))
