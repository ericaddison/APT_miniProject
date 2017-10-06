from google.appengine.ext import ndb
import source.Framework.Framework_Helpers as fh
from google.appengine.ext import blobstore


class Stream(ndb.Model):
    owner = ndb.KeyProperty(indexed=True, kind='StreamUser')
    name = ndb.StringProperty(indexed=True)
    coverImageURL = ndb.StringProperty(indexed=False)
    numViews = ndb.IntegerProperty(indexed=False)
    items = ndb.KeyProperty(indexed=False, kind='StreamItem', repeated=True)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
    viewList = ndb.DateTimeProperty(indexed=True, repeated=True)

    def add_item(self, item):
        self.items.append(item.key)
        self.put()

    def get_items(self, ind1, ind2):
        l = len(self.items)
        ind1, ind2 = sorted([ind1, ind2])
        ind1 = max(1, min(l, ind1))
        ind2 = max(1, min(l, ind2))
        item_keys = self.items[(ind1-1):ind2]
        return ndb.get_multi(item_keys), ind1, ind2

    def stream_id(self):
        return self.key.id()

    def get_owner_from_db(self):
        return self.owner.get()

    def get_id(self):
        return self.key.id()

    def delete(self):
        # delete the StreamTags associated with this stream
        StreamTag.delete_by_stream(self)

        # delete StreamSubscribers associated with this stream
        StreamSubscriber.delete_by_stream(self)

        # delete blobs owned by the items of this stream
        real_items = ndb.get_multi(self.items)
        [blobstore.delete(it.blobKey) for it in real_items if it.blobKey is not None]

        # delete the items owned by this stream
        ndb.delete_multi(self.items)

        # delete the stream itself
        self.key.delete()

    @classmethod
    # argument owner should be a StreamUser
    def create(cls, **kwargs):
        # gather arguments
        required_keys = ["name", "owner"]
        for key in required_keys:
            if "name" not in kwargs.keys():
                raise TypeError('Missing required key "{}"'.format(key))
        name = kwargs['name'].strip()
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
            return ndb.Key('Stream', long(stream_id)).get()
        except ValueError:
            return None

    @classmethod
    def get_batch_by_ids(cls, stream_ids):
        try:
            keys = [ndb.Key('Stream', long(st_id)) for st_id in stream_ids]
            return ndb.get_multi(keys)
        except ValueError:
            return None

    # owner should be a StreamUser
    @classmethod
    def get_ids_by_owner(cls, owner):
        stream_query0 = Stream.query()
        stream_query1 = stream_query0.filter(Stream.owner == owner.key)
        stream_result = stream_query1.fetch()
        if stream_result is None:
            return None
        return [s.key.id() for s in stream_result]


class StreamItem(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    owner = ndb.KeyProperty(indexed=True, kind='StreamUser')
    name = ndb.StringProperty(indexed=False)
    blobKey = ndb.BlobKeyProperty(indexed=False)
    URL = ndb.StringProperty(indexed=False)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

    def delete(self):
        # remove the blob
        self.blobKey.delete()

        # delete self
        self.key.delete()

    @classmethod
    def create(cls, **kwargs):
        # gather arguments
        required_keys = ["name", "owner", "URL", "stream"]
        for key in required_keys:
            if "name" not in kwargs.keys():
                raise TypeError('Missing required key "{}"'.format(key))
        name = kwargs['name']
        owner = kwargs['owner']
        url = kwargs['URL']
        stream = kwargs['stream']
        blob = kwargs['file'] if 'file' in kwargs.keys() else None

        # create and return stream
        item = StreamItem(
                owner=owner.key,
                blobKey=blob.key(),
                URL=url,
                name=name,
                stream=stream.key)
        item.put()
        return item


class Tag(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

    @classmethod
    def create(cls, tag_name):
        # tags are indexed in Datastore by their name
        tag_name = tag_name.strip()
        if Tag.get_by_name(tag_name):
            return None
        tag = Tag(name=tag_name, id=tag_name)
        tag.put()
        return tag

    @classmethod
    def get_by_name(cls, tag_name):
        if tag_name is None or tag_name == '':
            return None
        return ndb.Key('Tag', tag_name).get()

    @classmethod
    def get_key_from_name(cls, tag_name):
        print('MATHING KEY! ... ' + tag_name)
        key = ndb.Key('Tag', tag_name)
        return key


class StreamTag(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    tag = ndb.KeyProperty(indexed=True, kind='Tag')
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

    @classmethod
    # stream is a Stream object
    def get_by_stream(cls, stream):
        return StreamTag.query(StreamTag.stream == stream.key).fetch()

    @classmethod
    def delete_by_stream(cls, stream):
        stream_tags = StreamTag.query(StreamTag.stream == stream.key).fetch()
        keys = [st.key for st in stream_tags]
        ndb.delete_multi(keys)

    @classmethod
    # stream is a Stream object
    # tag is a Tag object
    def get_key_value(cls, stream, tag):
        return "{0}{1}".format(stream.key.id(), tag.key.id())

    @classmethod
    # stream is a Stream object
    # tag is a Tag object
    def get_key_value_with_tagname(cls, stream, tag):
        return "{0}{1}".format(stream.key.id(), tag)

    @classmethod
    def add_tags_to_stream(cls, stream, tag_name_list):
        tags = [Tag.create(tag) for tag in tag_name_list if tag not in [None, '']]
        [fh.searchablize_tag(tag) for tag in tags]
        streamtags = [StreamTag(stream=stream.key,
                                tag=Tag.get_key_from_name(tag),
                                id=StreamTag.get_key_value_with_tagname(stream, tag))
                      for tag in tag_name_list if tag not in [None, '']]
        ndb.put_multi(streamtags)


class StreamSubscriber(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    user = ndb.KeyProperty(indexed=True, kind='StreamUser')
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

    def get_id(self):
        return self.key.id()

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
    # stream is a Stream object
    # user is a StreamUser object
    def get_key_value(cls, stream, user):
        return "{0}{1}".format(user.key.id(), stream.key.id())

    @classmethod
    def get_key_value_by_ids(cls, stream_id, user_id):
        return "{0}{1}".format(user_id, stream_id)

    @classmethod
    def get_by_stream_and_user(cls, stream, user):
        key_val = StreamSubscriber.get_key_value(stream, user)
        return ndb.Key('StreamSubscriber', key_val).get()

    @classmethod
    def get_by_stream_id_and_user_id(cls, stream_id, user_id):
        key_val = StreamSubscriber.get_key_value_by_ids(stream_id, user_id)
        return ndb.Key('StreamSubscriber', key_val).get()

    @classmethod
    # stream is a Stream object
    def get_by_stream(cls, stream):
        return StreamSubscriber.query(StreamSubscriber.stream == stream.key).fetch()

    @classmethod
    # user is a StreamUser object
    def get_by_user(cls, user):
        return StreamSubscriber.query(StreamSubscriber.user == user.key).fetch()

    @classmethod
    def delete_by_stream(cls, stream):
        stream_tags = StreamSubscriber.query(StreamSubscriber.stream == stream.key).fetch()
        keys = [st.key for st in stream_tags]
        ndb.delete_multi(keys)

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

    def user_id(self):
        return self.key.id()
    
    def update_email_freq(self, freq):
        self.trendEmails = freq
        self.put()
        return freq
        
    
    @classmethod
    def get_by_id(cls, user_id):
        return ndb.Key('StreamUser', user_id).get()
