from google.appengine.ext import ndb
import webapp2
from NdbClasses import *


# create a test stream in the database
class TestStreamService(webapp2.RequestHandler):
    def get(self):


        # see if the owner user has already been created
        owner_email = 'tester@test.com'
        owner = StreamUser.query(StreamUser.email == owner_email).get()
        if not owner:
            owner = StreamUser(email=owner_email,
                               firstName='Test',
                               lastName='the Tester',
                               nickName='testy')
            owner.put()

        # see if this test stream has already been created
        result = Stream.query(Stream.owner == owner.key).get()
        if result:
            result.key.delete()

        # create a test stream
        stream = Stream(owner=owner.key,
                        name='Test Stream',
                        coverImageURL='https://www.google.com/imgres?imgurl=http%3A%2F%2Fxiostorage.com%2Fwp-content%2Fuploads%2F2015%2F10%2Ftest.png&imgrefurl=http%3A%2F%2Fxiostorage.com%2Feverythings-a-test-with-data-storage-performance%2F&docid=14F4Y2kGdoWxYM&tbnid=8mGjE0CA4qzyXM%3A&vet=10ahUKEwiBl4uRzs3WAhVK7yYKHXPpDlUQMwhIKAMwAw..i&w=640&h=562&client=ubuntu&bih=937&biw=1920&q=test&ved=0ahUKEwiBl4uRzs3WAhVK7yYKHXPpDlUQMwhIKAMwAw&iact=mrc&uact=8',
                        numViews=123454321,
                        items=[])

        key = stream.put()
        self.response.write(key)

        # insert some images
        item1 = StreamItem(stream=stream.key,
                           owner=owner.key,
                           blobKey=None,
                           URL='https://www.google.com/imgres?imgurl=http%3A%2F%2Fpngimg.com%2Fuploads%2Fnumber1%2Fnumber1_PNG14894.png&imgrefurl=http%3A%2F%2Fpngimg.com%2Fimgs%2Fnumbers%2Fnumber1%2F&docid=tqZ2Bxd_TL6aYM&tbnid=OqW3W2TTpY1NoM%3A&vet=10ahUKEwiy-_HTzs3WAhUIQCYKHbZeAaoQMwhAKAMwAw..i&w=400&h=400&client=ubuntu&bih=937&biw=1920&q=image%201&ved=0ahUKEwiy-_HTzs3WAhUIQCYKHbZeAaoQMwhAKAMwAw&iact=mrc&uact=8')
        item1.put()

        item2 = StreamItem(stream=stream.key,
                           owner=owner.key,
                           blobKey=None,
                           URL='https://www.google.com/imgres?imgurl=https%3A%2F%2Fstatic.r2r.io%2Fimages%2Frome2rio-2.png&imgrefurl=https%3A%2F%2Fwww.rome2rio.com%2F&docid=M5wQstW2JaTSPM&tbnid=BfCXdnqRRMyt2M%3A&vet=10ahUKEwiNreLozs3WAhUHbiYKHZhsAr8QMwhGKAowCg..i&w=400&h=400&client=ubuntu&bih=937&biw=1920&q=image%202&ved=0ahUKEwiNreLozs3WAhUHbiYKHZhsAr8QMwhGKAowCg&iact=mrc&uact=8')
        item2.put()

        item3 = StreamItem(stream=stream.key,
                           owner=owner.key,
                           blobKey=None,
                           URL='https://www.google.com/imgres?imgurl=https%3A%2F%2Fdesirefanatics.files.wordpress.com%2F2010%2F03%2F3-logo1.jpg&imgrefurl=https%3A%2F%2Fdesirefanatics.wordpress.com%2Ftag%2F3%2F&docid=PbHJDBlFB0HruM&tbnid=P4xD1JS0BBHt_M%3A&vet=10ahUKEwjvhZ_1zs3WAhWB5iYKHbk_DZIQMwhLKA8wDw..i&w=1456&h=1845&client=ubuntu&bih=937&biw=1920&q=image%203&ved=0ahUKEwjvhZ_1zs3WAhWB5iYKHbk_DZIQMwhLKA8wDw&iact=mrc&uact=8')
        item3.put()

        item4 = StreamItem(stream=stream.key,
                           owner=owner.key,
                           blobKey=None,
                           URL='https://www.google.com/imgres?imgurl=http%3A%2F%2Fcd1.dibujos.net%2Fdibujos%2Fpintar%2Fnumero-4.png&imgrefurl=https%3A%2F%2Fwww.tes.com%2Flessons%2FFGSnEt3m85I-Bg%2Fde-tafel-van-4&docid=oTok7MeDHV1eCM&tbnid=U5XbEpLWuciimM%3A&vet=10ahUKEwjUxfmEz83WAhVG4SYKHXkhBGMQMwg5KAMwAw..i&w=600&h=470&client=ubuntu&bih=937&biw=1920&q=image%204&ved=0ahUKEwjUxfmEz83WAhVG4SYKHXkhBGMQMwg5KAMwAw&iact=mrc&uact=8')
        item4.put()

        item5 = StreamItem(stream=stream.key,
                           owner=owner.key,
                           blobKey=None,
                           URL='https://www.google.com/imgres?imgurl=http%3A%2F%2Fwww.clker.com%2Fcliparts%2F7%2Fb%2F7%2F5%2F1194986875418362815creation_day_5_number_ge_02.svg.hi.png&imgrefurl=http%3A%2F%2Fwww.clker.com%2Fclipart-4639.html&docid=h1zgN_rJ0INMIM&tbnid=jlhPZUzz1g1awM%3A&vet=10ahUKEwjbm6KSz83WAhXI6iYKHZAeDdcQMwhHKBMwEw..i&w=348&h=593&client=ubuntu&bih=937&biw=1920&q=image%205&ved=0ahUKEwjbm6KSz83WAhXI6iYKHZAeDdcQMwhHKBMwEw&iact=mrc&uact=8')
        item5.put()


        # now update the stream list of images
        new_images = [item1.key, item2.key, item3.key, item4.key, item5.key]
        stream.items += new_images
        stream.put()



app = webapp2.WSGIApplication([
    ('/services/insertteststream', TestStreamService)
], debug=True)