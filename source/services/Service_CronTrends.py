from datetime import datetime
from datetime import timedelta
import webapp2

from google.appengine.api import mail
from source.models.NdbClasses import *
from source.services.Service_Utils import *


# Cron jobs for Trending service
# Every 5mins, go through all Stream.viewList timestamps and remove any which are older than 3hours.
# Every 5mins/1hr/1day, go through StreamUsers.trendEmails to get users emails and send out email with top trending Streams.
#
# If called without 'int' parameter, it will just cleanup the old stream views and return the top 3 trending streams.
#

class CronTrendsService(webapp2.RequestHandler):

    def trending(self, duration):
        #Cleanup old stream views:
        compareDateTime = datetime.now() - timedelta(hours=int(duration))
        oldStreams = Stream.query().filter(Stream.viewList <= compareDateTime).fetch()
           
        for stream in oldStreams:
            items = []
            for viewTime in stream.viewList:
                items.append(viewTime)
            for item in items:
                if item <= compareDateTime:
                    items.remove(item)
            stream.viewList = items
            stream.put()
        
        #Get the top 3 trending streams:
        allStreams = Stream.query().fetch()
        sortedStreams = sorted(allStreams, key=lambda x: len(x.viewList), reverse=True)

        top3StreamIDs = []
        for x in range(0,2):
            if sortedStreams[x]:
                stream = {'streamKeyID': sortedStreams[x].key.id(), 'recentViews': len(sortedStreams[x].viewList)}
                top3StreamIDs.append(stream)
                
        return top3StreamIDs
    
    def sendEmails(self, emailList):
        for email_rcpt_address in emailList:    
            try:
                mail.send_mail(sender=email_sender_address,
                           to=email_rcpt_address,
                           subject="WhiteTeam Trending Streams",
                           body="Check out these streams: {0}".format(trendingStreams))
            except:
                print "Email failed to: ", email_rcpt_address
                continue
                
        return
    
        
    def get(self):

        emails_sender_address = 'test@example.com'
        
        self.response.content_type = 'text/plain'
        response = {}
        
        intervalParam = self.request.get('int')
        
        #Default duration for "trending cleanup" is the previous 3 hours but can be overridden by parameter: 'duration'
        if self.request.get('duration'):
            trendingDuration = int(self.request.get('duration'))
        else:
            trendingDuration = 3

                        
        #/services/crontrends?int=5min
        if intervalParam == '5min':
            #Cleanup Stream.viewList entries, keep only those < 'trendingDuration' hrs old (default 3)
            print "Running scheduled 5min trending cleanup cron job"
            
            #Run cleanup and return list of top 3 trending StreamIDs
            trendingStreams = self.trending(trendingDuration)
            response['trendingStreams'] = trendingStreams

            
            #Collect StreamUser.email values for StreamUsers where StreamUser.trendEmails = '5min'
            userList = StreamUser.query().filter(StreamUser.trendEmails == '5min').fetch()
            userEmailList = []
            for user in userList:
                userEmailList.append(user.email)

            self.sendEmails(userEmailList)

                
        #/services/crontrends?int=1hr       
        if intervalParam == '1hr':
            #Collect StreamUser.email values for StreamUsers where StreamUser.trendEmails = '1hr'
            #Send trending email to those users
            trendingStreams = self.trending(trendingDuration)
            
            userList = StreamUser.query().filter(StreamUser.trendEmails == '1hr').fetch()
            userEmailList = []
            for user in userList:
                userEmailList.append(user.email)
                
            self.sendEmails(userEmailList)           
            
        #/services/crontrends?int=1day            
        if intervalParam == '1day':
            #Collect StreamUser.email values for StreamUsers where StreamUser.trendEmails = '1day'
            #Send trending email to those users
            trendingStreams = self.trending(trendingDuration)
            
            userList = StreamUser.query().filter(StreamUser.trendEmails == '1day').fetch()
            userEmailList = []
            for user in userList:
                userEmailList.append(user.email)  

            self.sendEmails(userEmailList)               

            
        #/services/crontrends    
        else:  #No intervalParam, assume the call just wants the trending streams:
            response['trendingStreams'] = self.trending(trendingDuration)


            
        self.response.write(json.dumps(response))


app = webapp2.WSGIApplication([
    ('/services/crontrends', CronTrendsService)
], debug=True)