
from google.appengine.api import app_identity
from google.appengine.api import users

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

import webapp2
import re
import os

#If we use Google Sign-in authentication
CLIENT_ID = "567910868038-rj3rdk31k9mbcf4ftder0rhfqr1vrld4.apps.googleusercontent.com"

class StreamUser(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    fname = ndb.StringProperty
    lname = ndb.StringProperty

class Stream(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    user = ndb.KeyProperty(kind=StreamUser)
    coverImageURL = ndb.StringProperty(indexed=False)
    numViews = ndb.IntegerProperty(indexed=False)

class StreamItem(ndb.Model):
    stream = ndb.KeyProperty(kind=Stream)
    name = ndb.StringProperty(indexed=False)
    image = ndb.BlobProperty(indexed=False)
    dateAdded = ndb.DateProperty(indexed=False)

class Tag(ndb.Model):
    name = ndb.StringProperty(indexed=True)

class StreamTag(ndb.Model):
    stream = ndb.KeyProperty(kind=Stream)
    tag = ndb.KeyProperty(kind=Tag)

class StreamSubscriber(ndb.Model):
    stream = ndb.KeyProperty(kind=Stream)
    user = ndb.KeyProperty(kind=StreamUser)
    
    
    

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
            
            
        else:
            login_url = users.create_login_url('/manage')
            login_text = 'Sign in'

        
        #NUCLEAR OPTION:
        #allSubs = StreamSubscriber.query()
        #for sub in allSubs:
        #    sub.key.delete()
        #    
        #allSubs = Stream.query()
        #for sub in allSubs:
        #    sub.key.delete()

        
        
        streamsOwn = Stream.query(Stream.user == user.email()) 
        streamKeysList = StreamSubscriber.query(StreamSubscriber.user == user.email())
        
        print "StreamKeysList = ", streamKeysList
        
        subbedStreams = []
        for streamKey in streamKeysList:
            subbedStreams.append(Stream.query(Stream.name == streamKey.stream.name).get())
            #print "streamKey = ", streamKey

        print "Streamkeyslist: ", streamKeysList

        template_values = {
            'user': user,
            'login_url': login_url,
            'login_text': login_text,
            'streams': streamsOwn,
            'subscribe': subbedStreams,
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
        
        subscriberArray = str(subscribers.split(";"))
        
        #print "tags = ", tags
        
        tagArray = str(tags.split(";"))
        
           
    
    
        #Create a new Stream entity then redirect to /view the new stream
        #id = streamname:email, this will be unique
        
        myKey = streamname + ":" + user.email()
        newStream = Stream(id = myKey, name=streamname, user=user.email(), coverImageURL=coverImageUrl, numViews=0)
        newStream.put()
        
        for subby in subscriberArray:
            newID = streamname + ":" + user.email()
            newSub = StreamSubscriber(id = newID, stream = newStream, user = user.email())
            newSub.put()
        
        for myTag in tagArray:
            newTag = Tag.get_or_insert(myTag)
            newStreamTag = StreamTag(stream = newStream, tag = newTag)
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


