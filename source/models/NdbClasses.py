import source.Framework.Framework_Helpers as fh
from google.appengine.ext import ndb
from google.appengine.ext import blobstore


class Stream(ndb.Model):
    owner = ndb.KeyProperty(indexed=True, kind='StreamUser')
    name = ndb.StringProperty(indexed=True)
    coverImageURL = ndb.StringProperty(indexed=False)
    numViews = ndb.IntegerProperty(indexed=False)
    items = ndb.KeyProperty(indexed=False, kind='StreamItem', repeated=True)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
    dateUpdated = ndb.DateTimeProperty(indexed=True, auto_now_add=True)
    viewList = ndb.DateTimeProperty(indexed=True, repeated=True)

    def add_item(self, item):
        self.dateUpdated = item.dateAdded
        self.items.insert(0, item.key)
        self.put()

    def get_items(self, ind1, ind2):
        l = len(self.items)
        ind1, ind2 = sorted([ind1, ind2])
        ind1 = max(1, min(l, ind1))
        ind2 = max(1, min(l, ind2))
        item_keys = self.items[(ind1-1):ind2]
        return ndb.get_multi(item_keys), ind1, ind2

    def get_all_items(self):
        return ndb.get_multi(self.items)

    def set_cover_image_url(self, url):
        self.coverImageURL = url
        self.put()

    def get_most_recent_image(self):
        if len(self.items) == 0:
            return None
        return self.items[-1].get()

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

    def get_meta_dict(self):
        return {
            'id': self.stream_id(),
            'owner': StreamUser.get_nickName_by_key(self.owner),
            'name': self.name,
            'coverImageURL': self.coverImageURL,
            'numViews': self.numViews,
            'numItems': len(self.items),
            'newestDate': str(self.dateUpdated),
            'dateAdded': str(self.dateAdded)
        }

    @classmethod
    # return a dictionary of the non-image information from this stream
    def get_meta_dict_by_id(cls, stream_id):
        stream = Stream.get_by_id(stream_id)
        if stream is None:
            return None
        return stream.get_meta_dict()

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

    @classmethod
    def get_all_names_and_ids(cls):
        stream_query0 = Stream.query()
        all_streams = stream_query0.fetch()
        return [(s.name, s.key.id()) for s in all_streams]

    @classmethod
    def get_all_streams(cls):
        return Stream.query().fetch()

    @classmethod
    def get_all_streams_by_updated(cls):
        return Stream.query().order(-cls.dateUpdated).fetch()


class StreamItem(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    owner = ndb.KeyProperty(indexed=True, kind='StreamUser')
    name = ndb.StringProperty(indexed=False)
    blobKey = ndb.BlobKeyProperty(indexed=False)
    URL = ndb.StringProperty(indexed=False)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
    longitude = ndb.StringProperty(indexed=False)
    latitude = ndb.StringProperty(indexed=False)

    def delete(self):
        # remove the blob
        self.blobKey.delete()

        # delete self
        self.key.delete()
        
    def getLatLng(self):
        if self.latitude is not None and self.longitude is not None and self.latitude.strip() != "" and self.longitude.strip() != "":
            dict = {'lat':str(self.latitude), 'lng':str(self.longitude)}
            return dict
        else:
            return None

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
        blobkey = blob.key() if blob is not None else None
        lat = kwargs['latitude']
        lng = kwargs['longitude']

        # create and return stream
        item = StreamItem(
                owner=owner.key,
                blobKey=blobkey,
                URL=url,
                name=name,
                stream=stream.key,
                latitude=lat,
                longitude=lng)
        item.put()
        return item


class Tag(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

    def delete(self):
        self.key.delete()

    @classmethod
    def create(cls, tag_name):
        if tag_name in ['', None]:
            return None
        tag_name = tag_name.lower().strip()
        # tags are indexed in Datastore by their name
        tag_name = tag_name.strip()
        if Tag.get_by_name(tag_name):
            return None
        tag = Tag(name=tag_name, id=tag_name)
        tag.put()
        return tag

    @classmethod
    def get_by_name(cls, tag_name):
        if tag_name in ['', None]:
            return None
        tag_name = tag_name.lower().strip()
        return ndb.Key('Tag', tag_name).get()

    @classmethod
    # also searchibilizes it
    def get_or_create_by_name(cls, tag_name):
        if tag_name in ['', None]:
            return None
        tag_name = tag_name.lower().strip()
        tag = cls.get_by_name(tag_name)
        if tag is not None:
            return tag
        tag = cls.create(tag_name)
        fh.searchablize_tag(tag, {})
        return tag

    @classmethod
    def get_key_from_name(cls, tag_name):
        if tag_name in ['', None]:
            return None
        tag_name = tag_name.lower().strip()
        tag_name = tag_name.strip().lower()
        key = ndb.Key('Tag', tag_name)
        return key

    @classmethod
    def get_all(cls):
        return Tag.query().fetch()


class StreamTag(ndb.Model):
    stream = ndb.KeyProperty(indexed=True, kind='Stream')
    tag = ndb.KeyProperty(indexed=True, kind='Tag')
    dateAdded = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

    def get_tag_name(self):
        return self.tag.id()

    def get_stream_id(self):
        return self.stream.id()

    @classmethod
    # stream is a Stream object
    def get_batch_by_stream(cls, stream):
        return StreamTag.query(StreamTag.stream == stream.key).fetch()

    @classmethod
    # tag_name is a string
    def get_batch_by_tag_name(cls, tag_name):
        if tag_name in ['', None]:
            return None
        tag_name = tag_name.lower().strip()
        return StreamTag.query(StreamTag.tag == Tag.get_key_from_name(tag_name)).fetch()

    @classmethod
    # stream is a Stream object
    # tag is a tag object
    def get_by_stream_and_tag(cls, stream, tag):
        return cls.get_key(stream, tag).get()

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
    # tag is a tag name
    def get_key_value_with_tagname(cls, stream, tag_name):
        if tag_name in ['', None]:
            return None
        tag_name = tag_name.lower().strip()
        return "{0}{1}".format(stream.key.id(), tag_name.strip())

    @classmethod
    # stream is a Stream object
    # tag is a Tag object
    def get_key(cls, stream, tag):
        return ndb.Key('StreamTag', cls.get_key_value(stream, tag))

    @classmethod
    def add_tags_to_stream_by_name(cls, stream, tag_name_list):
        tag_name_list = [tag_name.strip().lower() for tag_name in tag_name_list if tag_name not in [None, '']]
        tags = [Tag.create(tag_name) for tag_name in tag_name_list if tag_name not in [None, '']]
        [fh.searchablize_tag(tag) for tag in tags]
        streamtags = [StreamTag(stream=stream.key,
                                tag=Tag.get_key_from_name(tag_name),
                                id=StreamTag.get_key_value_with_tagname(stream, tag_name))
                      for tag_name in tag_name_list if tag_name not in [None, '']]
        ndb.put_multi(streamtags)

    @classmethod
    def delete_tag_from_stream(cls, stream, tag):
        cls.get_key(stream, tag).delete()


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

    @classmethod
    def get_nickName_by_key(cls, user_key):
        return user_key.get().nickName
