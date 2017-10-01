
from google.appengine.api import app_identity
from google.appengine.api import users

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

from NdbClasses import *
import webapp2
import os

import datetime

#If we use Google Sign-in authentication
CLIENT_ID = "567910868038-rj3rdk31k9mbcf4ftder0rhfqr1vrld4.apps.googleusercontent.com"
    

class MainPage(webapp2.RequestHandler):
    def get(self):
        
        user = users.get_current_user()
        
        print "MainPage: users.get_current_user(): ", user
        
        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
            
        else:
            login_url = users.create_login_url('/manage')
            login_text = 'Sign in'

        template_values = {
            'user': user,
            'login_url': login_url,
            'login_text': login_text,
            'app': app_identity.get_application_id()}

        self.response.content_type = 'text/html'
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        
        
class ManagePage(webapp2.RequestHandler):
    def get(self):
    
        user = users.get_current_user()

        
        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
            
            #Check to see if user is present in StreamUser table, if not add them.
            stream_user = ndb.Key('StreamUser',user.user_id()).get()
            email_dup_check = len(StreamUser.query(StreamUser.email == user.email()).fetch())!=0
            
            print "ManagePage: stream_user: ", stream_user
            print "ManagePage: email_dup_check: ", email_dup_check
            
            if not stream_user:
                if email_dup_check:
                    self.response.write("Uh oh! Duplicate email!!!")
                    return
                print("\n\nAdding new StreamUser by email: {}\n\n".format(str(user.email())))
                stream_user = StreamUser(email = user.email(), nickName = nickname, id=user.user_id())
                stream_user.put()

        else:
            self.redirect("/")
            return

        # get streams owned by this user
        myuser = ndb.Key('StreamUser', stream_user.key.id())
        user_streams = Stream.query(Stream.owner == myuser).fetch()
        print("\nstreams owned by {0}: {1}".format(str(user.nickname()), str(user_streams)))
        
        
        owned_streams = []

        for parentStream in user_streams:
            print "parentStream: ", parentStream
            streamItems = StreamItem.query(StreamItem.stream == parentStream.key).fetch()
            counter =  0
            newestItemDate = datetime.date(1900,1, 1)
            streamDict = {}
            for item in streamItems:
                thisStream = Stream.query(Stream.key.id() == streamID).get()
                counter += 1
                if item.dateAdded > newestItemDate:
                    newestItemDate = item.dateAdded
            streamDict = {'streamName': parentStream.name, 'counter': counter, 'newestDate': newestItemDate, 'key': parentStream.key.id()}
            owned_streams.append(streamDict)
        
        
        

        # get streams subscribed by this user
        #user_subscriptions = StreamSubscriber.query(StreamSubscriber.user == stream_user.key).fetch()
        user_subscriptions = Stream.query(Stream.subscribers == stream_user.key).fetch()
        print("\nstreams subscribed to by {0}: {1}".format(user.nickname(), user_subscriptions))
        
        subbed_streams = []

        for parentStream in user_subscriptions:
            streamItems = StreamItem.query(StreamItem.stream == parentStream.key).fetch()
            counter =  0
            newestItemDate = datetime.date(1900,1, 1)
            streamDict = {}
            for item in streamItems:
                counter += 1
                if item.dateAdded > newestItemDate:
                    newestItemDate = item.dateAdded
            streamDict = {'streamName': parentStream.name, 'counter': counter, 'newestDate': newestItemDate, 'views': parentStream.numViews, 'key': parentStream.key.id()}
            subbed_streams.append(streamDict)
        
        print "owned_streams: ", owned_streams
        print "subbed_streams: ", subbed_streams

        template_values = {
            'user': user,
            'isAdmin': users.IsCurrentUserAdmin(),
            'login_url': login_url,
            'login_text': login_text,
            'streams': owned_streams,
            'subscribe': subbed_streams,
            'app': app_identity.get_application_id()}

        self.response.content_type = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'manage.html')
        self.response.write(template.render(path, template_values))
        

class CreatePage(webapp2.RequestHandler):
    def post(self):

        user = users.get_current_user()

        streamname = self.request.get('streamname')
        subscribers = self.request.get('subs')
        tags = self.request.get('tags')
        coverImageUrl = self.request.get('coverUrl')
        myStreamUser = StreamUser.query(StreamUser.key==ndb.Key('StreamUser',user.user_id())).get()
        
        
        subscriberArray = subscribers.split(";") 
        tagArray = tags.split(";")

        subUserArray = StreamUser.query(StreamUser.email.IN(subscriberArray)).fetch()
        subUserKeyArray = []
        for myuser in subUserArray:
            subUserKeyArray.append(myuser.key)
        
        
        #Create a new Stream entity then redirect to /view the new stream
        newStream = Stream(name=streamname, owner=myStreamUser.key, coverImageURL=coverImageUrl, numViews=0, subscribers=subUserKeyArray, tags=tagArray)
        newStream.put()
        
       
        #Redirect to /view for this stream
        self.redirect('/manage')
    
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
            'user': user,
            'login_url': login_url,
            'login_text': login_text,
            'app': app_identity.get_application_id()}


        self.response.content_type = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'create.html')
        self.response.write(template.render(path, template_values))        
        

        
        
class ViewPage(webapp2.RequestHandler):
    def post(self):
        
        #User will be adding a new image to the stream.
        #GET the values they POSTED, create the new StreamItem, then redirect back to '/view?id=<<streamKeyID>>'
        return
    
    
    def get(self):
    
        user = users.get_current_user()

        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        
        streamID = self.request.get('id')

        allStreams = Stream.query().fetch()
        all_streams = []


        for parentStream in allStreams:
            streamItems = StreamItem.query(StreamItem.stream == parentStream.key).fetch()
            counter =  0
            newestItemDate = datetime.date(1900,1, 1)
            streamDict = {}
            for item in streamItems:
                counter += 1
                if item.dateAdded > newestItemDate:
                    newestItemDate = item.dateAdded
            streamDict = {'streamName': parentStream.name, 'counter': counter, 'newestDate': newestItemDate, 'views': parentStream.numViews, 'key': parentStream.key.id()}
            all_streams.append(streamDict)

            
        thisStream = None            
        if streamID != "":    
            streamKey = ndb.Key('Stream', int(streamID))
        
            print "ViewPage: streamID = ", streamID
        
            thisStream = Stream.get_by_id(int(streamID))
            streamItems = StreamItem.query(StreamItem.stream == streamKey).fetch()
        
            #Increment the numViews counter on the Stream object.
            thisStream.numViews = thisStream.numViews + 1
            thisStream.put()
        
        
        
        #TODO:  Add form to let user add a new image to this stream.  Then reload page to display the updated stream


        template_values = {
            'user': user,
            'isAdmin': users.IsCurrentUserAdmin(),
            'login_url': login_url,
            'login_text': login_text,
            'thisStream': thisStream,
            'streams': all_streams,
            'app': app_identity.get_application_id()}

        self.response.content_type = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'view.html')
        self.response.write(template.render(path, template_values))        
        
        
        
# define the "app" that will be referenced from app.yaml
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/manage', ManagePage),
    ('/create', CreatePage),
    ('/view', ViewPage)
], debug=True)


