from google.appengine.ext import ndb


class Stream(ndb.Model):
    owner = ndb.KeyProperty(indexed=True, kind='StreamUser')
    name = ndb.StringProperty(indexed=False)
    coverImageURL = ndb.StringProperty(indexed=False)
    numViews = ndb.IntegerProperty(indexed=False)
    items = ndb.KeyProperty(indexed=False, kind='StreamItem', repeated=True)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
    viewList = ndb.DateTimeProperty(indexed=True, repeated=True)


class StreamItem(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    owner = ndb.KeyProperty(indexed=True, kind='StreamUser')
    name = ndb.StringProperty(indexed=False)
    blobKey = ndb.BlobKeyProperty(indexed=False)
    URL = ndb.StringProperty(indexed=False)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)


class Tag(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

    @classmethod
    def create_tag(cls, tag_name):
        if ndb.Key('Tag', tag_name).get():
            return None
        tag = Tag(name=tag_name, id=tag_name)
        tag.put()
        return tag

    @classmethod
    def get_tag_by_name(cls, tag_name):
        return ndb.Key('Tag', tag_name).get()



class StreamTag(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    tag = ndb.KeyProperty(indexed=True, kind='Tag')
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)


class StreamSubscriber(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    user = ndb.KeyProperty(indexed=True, kind='StreamUser')
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)


class StreamUser(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    firstName = ndb.StringProperty(indexed=False)
    lastName = ndb.StringProperty(indexed=False)
    nickName = ndb.StringProperty(indexed=False)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
    trendEmails = ndb.StringProperty(indexed=True)
