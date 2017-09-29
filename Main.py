
from google.appengine.api import app_identity
from google.appengine.api import users

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

from NdbClasses import *
import webapp2
import os

#If we use Google Sign-in authentication
CLIENT_ID = "567910868038-rj3rdk31k9mbcf4ftder0rhfqr1vrld4.apps.googleusercontent.com"
    

class MainPage(webapp2.RequestHandler):
    def get(self):
        
        user = users.get_current_user()
        
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
        user_streams = Stream.query(Stream.owner == stream_user.key).fetch()
        print("\nstreams owned by {0}: {1}".format(str(user.nickname()), str(user_streams)))

        # get streams subscribed by this user
        user_subscriptions = StreamSubscriber.query(StreamSubscriber.user == stream_user.key).fetch()
        print("\nstreams subscribed to by {0}: {1}".format(user.nickname(), user_subscriptions))

        template_values = {
            'user': user,
            'isAdmin': users.IsCurrentUserAdmin(),
            'login_url': login_url,
            'login_text': login_text,
            'streams': user_streams,
            'subscribe': user_subscriptions,
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

        #Create a new Stream entity then redirect to /view the new stream
        newStream = Stream(name=streamname, owner=myStreamUser.key, coverImageURL=coverImageUrl, numViews=0)
        newStream.put()
        
        print "len(subscriberArray) = ", len(subscriberArray)
        
        for subby in subscriberArray:
            print "subby = ", subby
            myUser = StreamUser.query(StreamUser.email == subby).get()
            if myUser:
                newSub = StreamSubscriber(stream = newStream.key, user = myUser.key)
                newSub.put()
            else:
                print("\nNo user found with email {}".format(subby))

        print("\n\ntags = {}\n\n".format(tagArray))

        for myTag in tagArray:
            if myTag:
                newTag = Tag.get_or_insert(myTag)
                newStreamTag = StreamTag(stream = newStream.key, tag = newTag.key)
                newStreamTag.put()
            
        #Redirect to /view for this stream
        self.redirect('/manage')
    
    def get(self):
    
        user = users.get_current_user()
        
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
        path = os.path.join(os.path.dirname(__file__), 'create.html')
        self.response.write(template.render(path, template_values))        
        

# define the "app" that will be referenced from app.yaml
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/manage', ManagePage),
    ('/create', CreatePage)
], debug=True)


