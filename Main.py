
from google.appengine.api import app_identity
from google.appengine.api import users

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

import webapp2
import re
import os

#If we use Google Sign-in authentication
CLIENT_ID = "567910868038-rj3rdk31k9mbcf4ftder0rhfqr1vrld4.apps.googleusercontent.com"

class Stream(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    user = ndb.StringProperty(indexed=True)
    coverImageURL = ndb.StringProperty(indexed=False)
    numViews = ndb.IntegerProperty(indexed=False)

class StreamItem(ndb.Model):
    stream = ndb.StructuredProperty(Stream)
    name = ndb.StringProperty(indexed=False)
    image = ndb.BlobProperty(indexed=False)
    dateAdded = ndb.DateProperty(indexed=False)

class Tag(ndb.Model):
    name = ndb.StringProperty(indexed=False)

class StreamTag(ndb.Model):
    stream = ndb.StructuredProperty(Stream)
    tag = ndb.StructuredProperty(Tag)

class StreamSubscriber(ndb.Model):
    stream = ndb.StructuredProperty(Stream)
    user = ndb.StringProperty(indexed=True)
    
    
    

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
        else:
            login_url = users.create_login_url('/manage')
            login_text = 'Sign in'

        #Need to pull a list of streams owned by 'user'
        #and a list of streams which 'user' subscribes to.
        #Display both on the management page.
        
        streams = Stream.query(Stream.user == user.email()) 

        template_values = {
            'user': user,
            'login_url': login_url,
            'login_text': login_text,
            'streams': streams,
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
        
        subscriberArray = subscribers.split(";")
        
        #print "tags = ", tags
        
        tagArray = str(tags.split(";"))
        
       
        #Create a new Stream entity then redirect to /view the new stream
        #id = streamname:email, this will be unique
        
        myKey = streamname + ":" + user.email()
        newStream = Stream(id = myKey, name=streamname, user=user.email(), coverImageURL=coverImageUrl, numViews=0)
        newStream.put()
        
        for myTag in tagArray:
            newTag = Tag.get_or_insert(myTag)
            newStreamTag = StreamTag(stream = newStream, tag = newTag)
            newStreamTag.put()
            
        #Redirect to /view for this stream
    
    
    def get(self):
    
        user = users.get_current_user()
        
        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
        else:
            login_url = users.create_login_url('/manage')
            login_text = 'Sign in'

        #Need to pull a list of streams owned by 'user'
        #and a list of streams which 'user' subscribes to.
        #Display both on the management page.

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


