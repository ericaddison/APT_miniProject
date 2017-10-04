import os
import json
import webapp2
import urllib
import urllib2

from google.appengine.api import app_identity
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

from Framework.Framework_Helpers import stream_name_parm, cover_url_parm, tags_parm, subscribers_parm
from Framework.Framework_Helpers import get_request_parameter_dictionary, write_response

from source.models.NdbClasses import *

# If we use Google Sign-in authentication
CLIENT_ID = "567910868038-rj3rdk31k9mbcf4ftder0rhfqr1vrld4.apps.googleusercontent.com"


class MainPage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()

        print
        "MainPage: users.get_current_user(): ", user

        if user:
            nickname = user.nickname()
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


class ManagePage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()

        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'

            # Check to see if user is present in StreamUser table, if not add them.
            stream_user = ndb.Key('StreamUser', user.user_id()).get()
            email_dup_check = len(StreamUser.query(StreamUser.email == user.email()).fetch()) != 0

            print
            "ManagePage: stream_user: ", stream_user
            print
            "ManagePage: email_dup_check: ", email_dup_check

            if not stream_user:
                if email_dup_check:
                    self.response.write("Uh oh! Duplicate email!!!")
                    return
                print("\n\nAdding new StreamUser by email: {}\n\n".format(str(user.email())))
                stream_user = StreamUser(email=user.email(), nickName=nickname, id=str(user.user_id()))
                stream_user.put()

        else:
            self.redirect("/")
            return

        # get streams owned by this user
        myuser = ndb.Key('StreamUser', stream_user.key.id())
        user_streams = Stream.query(Stream.owner == myuser).fetch()
        print("\nstreams owned by {0}: {1}".format(str(user.nickname()), str(user_streams)))

        owned_streams = []

        for stream in user_streams:
            print("parentStream: {}".format(stream))
            newestDate = ""
            if len(stream.items) > 0:
                newestDate = ndb.Key('StreamItem', stream.items[-1].id()).get().dateAdded
            streamDict = {'streamName': stream.name, 'counter': len(stream.items), 'newestDate': newestDate,
                          'id': stream.key.id()}
            owned_streams.append(streamDict)

        # get streams subscribed by this user
        user_subscriptions = StreamSubscriber.query(StreamSubscriber.user == stream_user.key).fetch()
        print("\nstreams subscribed to by {0}: {1}".format(user.nickname(), user_subscriptions))

        subbed_streams = []

        for stream in user_streams:
            print("parentStream: {}".format(stream))
            newestDate = ""
            if len(stream.items) > 0:
                newestDate = ndb.Key('StreamItem', stream.items[-1].id()).get().dateAdded
            streamDict = {'streamName': stream.name, 'counter': len(stream.items), 'newestDate': newestDate,
                          'id': stream.key.id(), 'views': stream.numViews}
            subbed_streams.append(streamDict)

        print("owned_streams: {}".format(owned_streams))
        print("subbed_streams: {}".format(subbed_streams))

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user,
            'isAdmin': users.IsCurrentUserAdmin(),
            'login_url': login_url,
            'login_text': login_text,
            'streams': owned_streams,
            'subscribe': subbed_streams,
            'app': app_identity.get_application_id()}

        self.response.content_type = 'text/html'
        path = os.path.join(os.path.dirname(__file__), '../templates/Manage.html')
        self.response.write(template.render(path, template_values))


class CreatePage(webapp2.RequestHandler):
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
            'stream_name_parm': stream_name_parm,
            'tags_parm': tags_parm,
            'cover_url_parm': cover_url_parm,
            'subs_parm': subscribers_parm
            }

        self.response.content_type = 'text/html'
        path = os.path.join(os.path.dirname(__file__), '../templates/Create.html')
        self.response.write(template.render(path, template_values))

    def post(self):
        # make call to createStream service
        parm_dict = get_request_parameter_dictionary(self)
        create_stream_url = 'http://{0}/services/createstream?{1}'.format(os.environ['HTTP_HOST'], urllib.urlencode(parm_dict))
        print("\n\n{}\n\n".format(create_stream_url))
        result = urllib2.urlopen(create_stream_url)
        response = json.loads("".join(result.readlines()))
        write_response(self, response)


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
    ('/manage', ManagePage),
    ('/create', CreatePage),
    ('/view', ViewAllStreamsPage)
], debug=True)
