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

        user = fh.get_current_user(self)

        if user:
            login_url = fh.get_logout_url(self, '/')
            login_text = 'Sign out'
            name = user.nickName

        else:
            login_url = fh.get_login_url(self, '/manage')
            login_text = 'Sign in'
            name = ""

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': name,
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

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user,
            'user_id': user.user_id(),
            'isAdmin': users.IsCurrentUserAdmin(),
            'login_url': login_url,
            'login_text': login_text,
            'app': app_identity.get_application_id()
        }

        # look for any message
        msg = self.get_request_param(fh.message_parm)
        if msg not in [None, '']:
            template_values['msg'] = msg

        self.response.content_type = 'text/html'
        path = os.path.join(os.path.dirname(__file__), '../templates/Manage.html')
        self.response.write(template.render(path, template_values))


class TrendingPage(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        stream_user = ndb.Key('StreamUser', user.user_id()).get()

        param_string = self.request.get('freq')

        stream_user.update_email_freq(param_string)

        self.redirect("/trending")

    def get(self):

        user = users.get_current_user()

        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        response = urllib2.urlopen('http://{0}/services/crontrends'.format(os.environ['HTTP_HOST']))
        returnValue = json.loads("".join(response.readlines()))

        streamList = []
        for stream in returnValue.get('trendingStreams'):
            thisStream = Stream.get_by_id(stream.get('streamKeyID'))
            streamDict = {'stream': thisStream, 'trendViews': int(stream.get('recentViews')),
                          'id': thisStream.key.id()}
            streamList.append(streamDict)

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user,
            'login_url': login_url,
            'login_text': login_text,
            'trendingStreams': streamList,
            'app': app_identity.get_application_id()}

        self.response.content_type = 'text/html'
        path = os.path.join(os.path.dirname(__file__), '../templates/Trends.html')
        self.response.write(template.render(path, template_values))


# define the "app" that will be referenced from app.yaml
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/trending', TrendingPage)
], debug=True)
