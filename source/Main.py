import os
import json
import webapp2
import urllib
import urllib2

from google.appengine.api import app_identity
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

import Framework.Framework_Helpers as fh

from source.models.NdbClasses import *

from source.Framework.BaseHandler import BaseHandler

# If we use Google Sign-in authentication
CLIENT_ID = "567910868038-rj3rdk31k9mbcf4ftder0rhfqr1vrld4.apps.googleusercontent.com"


class MainPage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()

        if user:
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'

        else:
            login_url = users.create_login_url('/manage')
            login_text = 'Sign in'

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user,
            'login_url': login_url,
            'login_text': login_text,
            'app': app_identity.get_application_id()}

        self.response.content_type = 'text/html'

        path = os.path.join(os.path.dirname(__file__), '../templates/Index.html')
        self.response.out.write(template.render(path, template_values))


class ManagePage(BaseHandler):
    def get(self):

        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'

            # Check to see if user is present in StreamUser table, if not add them.
            stream_user = ndb.Key('StreamUser', user.user_id()).get()
            email_dup_check = len(StreamUser.query(StreamUser.email == user.email()).fetch()) != 0

            if not stream_user:
                if email_dup_check:
                    self.response.write("Uh oh! Duplicate email!!!")
                    return
                stream_user = StreamUser(email=user.email(), nickName=nickname, id=str(user.user_id()))
                stream_user.put()

        else:
            self.redirect("/")
            return

        # call management service to get stream lists
        management_service_url = 'http://{0}/services/management?{1}={2}'.format(os.environ['HTTP_HOST'],
                                                                                 fh.user_id_parm, user.user_id())
        print("\n\n{}\n\n".format(management_service_url))
        result = urllib2.urlopen(management_service_url)
        response = json.loads("".join(result.readlines()))
        user_streams = response['owned_streams']
        subby_streams = response['subscribed_streams']

        owned_streams = []
        for stream_id in user_streams:
            stream = Stream.get_by_id(stream_id)
            newestDate = ""
            if len(stream.items) > 0:
                newestDate = ndb.Key('StreamItem', stream.items[-1].id()).get().dateAdded
            streamDict = {'streamName': stream.name, 'counter': len(stream.items), 'newestDate': newestDate,
                          'id': stream.key.id()}
            owned_streams.append(streamDict)

        # get streams subscribed by this user
        subbed_streams = []
        for stream_id in subby_streams:
            stream = Stream.get_by_id(stream_id)
            newestDate = ""
            if len(stream.items) > 0:
                newestDate = ndb.Key('StreamItem', stream.items[-1].id()).get().dateAdded
            streamDict = {'streamName': stream.name, 'counter': len(stream.items), 'newestDate': newestDate,
                          'id': stream.key.id(), 'views': stream.numViews}
            subbed_streams.append(streamDict)

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user,
            'isAdmin': users.IsCurrentUserAdmin(),
            'login_url': login_url,
            'login_text': login_text,
            'streams': owned_streams,
            'subscribe': subbed_streams,
            'app': app_identity.get_application_id()
        }

        # look for any message
        msg = self.get_request_param(fh.message_parm)
        if msg not in [None, '']:
            template_values['msg'] = msg

        self.response.content_type = 'text/html'
        path = os.path.join(os.path.dirname(__file__), '../templates/Manage.html')
        self.response.write(template.render(path, template_values))


class ViewAllStreamsPage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()

        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user,
            'login_url': login_url,
            'login_text': login_text,
            'app': app_identity.get_application_id()}

        self.response.content_type = 'text/html'
        path = os.path.join(os.path.dirname(__file__), '../templates/ViewAll.html')
        self.response.write(template.render(path, template_values))


# define the "app" that will be referenced from app.yaml
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/view', ViewAllStreamsPage)
], debug=True)
