from google.appengine.ext import ndb


class Stream(ndb.Model):
    owner = ndb.KeyProperty(indexed=True, kind='StreamUser')
    name = ndb.StringProperty(indexed=True)
    coverImageURL = ndb.StringProperty(indexed=False)
    numViews = ndb.IntegerProperty(indexed=False)
    items = ndb.KeyProperty(indexed=False, kind='StreamItem', repeated=True)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
    viewList = ndb.DateTimeProperty(indexed=True, repeated=True)

    @classmethod
    # argument owner should be a StreamUser
    def create(cls, **kwargs):
        # gather arguments
        required_keys = ["name", "owner"]
        for key in required_keys:
            if "name" not in kwargs.keys():
                raise TypeError('Missing required key "{}"'.format(key))
        name = kwargs['name']
        owner = kwargs['owner']
        cover_url = kwargs['cover_url'] if 'cover_url' in kwargs.keys() else None

        # check for existing stream
        if Stream.get_by_owner_and_name(owner, name):
            return None

        # create and return stream
        stream = Stream(name=name,
                        owner=owner.key,
                        coverImageURL=cover_url,
                        numViews=0,
                        items=[],
                        viewList=[])
        stream.put()
        return stream

    @classmethod
    # owner should be a StreamUser
    # name should be a string
    def get_by_owner_and_name(cls, owner, name):
        query0 = Stream.query()
        query1 = query0.filter(Stream.owner == owner.key)
        query2 = query1.filter(Stream.name == name)
        return query2.get()

    @classmethod
    def get_by_id(cls, stream_id):
        try:
            return ndb.Key('Stream', int(stream_id)).get()
        except ValueError, e:
            return None


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
    def create(cls, tag_name):
        # tags are indexed in Datastore by their name
        if Tag.get_by_name(tag_name):
            return None
        tag = Tag(name=tag_name, id=tag_name)
        tag.put()
        return tag

    @classmethod
    def get_by_name(cls, tag_name):
        return ndb.Key('Tag', tag_name).get()


class StreamTag(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    tag = ndb.KeyProperty(indexed=True, kind='Tag')
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)


class StreamSubscriber(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    user = ndb.KeyProperty(indexed=True, kind='StreamUser')
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

    @classmethod
    # stream is a Stream object
    # user is a StreamUser object
    def get_key_value(cls, stream, user):
        return "{0}{1}".format(user.key.id(), stream.key.id())

    @classmethod
    def get_by_stream_and_user(cls, stream, user):
        key_val = StreamSubscriber.get_key_value(stream, user)
        return ndb.Key('StreamSubscriber', key_val).get()

    @classmethod
    def create(cls, stream, user):
        sub = StreamSubscriber.get_by_stream_and_user(stream, user)
        if sub is not None:
            return None
        key_val = StreamSubscriber.get_key_value(stream, user)
        sub = StreamSubscriber(user=user.key,
                               stream=stream.key,
                               id=key_val)
        sub.put()
        return sub

    @classmethod
    def delete(cls, stream, user):
        sub = StreamSubscriber.get_by_stream_and_user(stream, user)
        if sub is None:
            return False
        sub.key.delete()
        return True


    @classmethod
    # add subscribers to a stream from a list of email strings
    def add_subscribers_by_emails(cls, stream, sub_list):
        # look for users associated with the emails in sub_list
        stripped_emails = [email.strip() for email in sub_list]
        subbers = StreamUser.query(StreamUser.email.IN(stripped_emails))
        new_subs = [StreamSubscriber(stream=stream.key,
                                     user=subber.key,
                                     id=StreamSubscriber.get_key_value(stream, subber)
                                     )
                    for subber in subbers]
        ndb.put_multi(new_subs)
        return len(new_subs)


class StreamUser(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    firstName = ndb.StringProperty(indexed=False)
    lastName = ndb.StringProperty(indexed=False)
    nickName = ndb.StringProperty(indexed=False)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
    trendEmails = ndb.StringProperty(indexed=True)
