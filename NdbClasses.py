from google.appengine.ext import ndb


class Stream(ndb.Model):
    owner = ndb.KeyProperty(indexed=True, kind='StreamUser')
    name = ndb.StringProperty(indexed=False)
    coverImageURL = ndb.StringProperty(indexed=False)
    numViews = ndb.IntegerProperty(indexed=False)


class StreamItem(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    owner = ndb.KeyProperty(indexed=True, kind='User')
    name = ndb.StringProperty(indexed=False)
    blobKey = ndb.BlobKeyProperty(indexed=False)
    URL = ndb.StringProperty(indexed=False)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)


class Tag(ndb.Model):
    name = ndb.StringProperty(indexed=False)


class StreamTag(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    tag = ndb.KeyProperty(indexed=True, kind='Tag')


class StreamSubscriber(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    user = ndb.KeyProperty(indexed=True, kind='StreamUser')


class StreamUser(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    firstName = ndb.StringProperty(indexed=False)
    lastName = ndb.StringProperty(indexed=False)
    nickName = ndb.StringProperty(indexed=False)
