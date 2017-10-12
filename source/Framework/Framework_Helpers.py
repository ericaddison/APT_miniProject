import json
import re
import datetime
import urllib2

import webapp2
from google.appengine.api import images
from google.appengine.api import search
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

# [START HTTP request parameter names]
stream_id_parm = 'streamID'
stream_name_parm = 'streamname'
user_id_parm = 'userID'
image_range_parm = 'imageRange'
tag_name_parm = 'tagName'
search_string_parm = 'searchString'
search_results_parm = 'searchResults'
subscribers_parm = 'subs'
tags_parm = 'tags'
cover_url_parm = 'coverUrl'
redirect_parm = 'redirect'
error_code_parm = 'code'
message_parm = 'msg'
owner_parm = 'owner'
num_images_parm = 'num_images'
url_parm = 'url'
autocomplete_parm = 'term'
active_image_parm = 'activeImage'
# [END HTTP request parameter names]

# [START ERROR CODES]
error_codes = {
    111: 'Stream view already exists! Please choose another name!'
}
# [END ERROR CODES]


search_index_namespace = 'connexion'


class SearchInfo(ndb.Model):
    tag_index_name = ndb.StringProperty()
    stream_index_name = ndb.StringProperty()


# [START HTTP request methods]
# currently using webapp2 request handlers


def get_site_url(path, **kwargs):
    webapp2.uri_for(path, **kwargs)


def bad_request_error(handler, response_dict, error_msg):
    response_dict['error'] = error_msg
    handler.response.set_status(400)
    handler.response.write(json.dumps(response_dict))
    return

# [END HTTP request methods]


# [START file handling]
# currently using blobstore and images API for file handling

def get_upload_from_filehandler(filehandler, index):
    if 0 <= index < len(filehandler.get_uploads()):
        return filehandler.get_uploads()[index]
    return None


def get_file_url(myfile):
    return images.get_serving_url(myfile.key())

# [END file handling]


# returns the current google user for now
# but could be extended to work with non-google user types
# e.g. Facebook login, plain email login, etc
# return a StreamUser
def get_current_user(handler):
    # get google user
    google_user = users.get_current_user()

    if google_user is None:
        return None

    # look up our user
    stream_user = ndb.Key('StreamUser', google_user.user_id()).get()

    # return
    return stream_user


def get_logout_url(handler, redirect):
    return users.create_logout_url(redirect)


def get_login_url(handler, redirect):
    return users.create_login_url(redirect)


def searchablize_tag(tag, response={}):
    searchablize_tag_or_stream(tag, get_tag_index_name(), response)


def searchablize_stream(stream, response={}):
    searchablize_tag_or_stream(stream, get_stream_index_name(), response)


def search_tag_index(search_string):
    index = get_tag_index()
    search_results = index.search("string: {}".format(search_string))
    tags = set()
    for res in search_results:
        for fld in res.fields:
            if fld.name == "id":
                tags.add(fld.value)
    return list(tags)


def search_tag_index_alpha(search_string, limit):
    index = get_tag_index()
    search_results = index.search(
                        query=search.Query(
                            "string: {}".format(search_string),
                            options=search.QueryOptions(
                                limit=limit,
                                sort_options=search.SortOptions(
                                    expressions=[
                                        search.SortExpression(expression='id', default_value='')],
                                    limit=1000),
                                returned_fields=['id']
                            )
                        )
                    )
    tags = set()
    for res in search_results:
        tags.add(res.fields[0].value)
    return list(tags)


# returns list of stream IDs of matching strings
def search_stream_index(search_string):
    index = get_stream_index()
    search_results = index.search("string: {}".format(search_string))
    streams = set()
    for res in search_results:
        for fld in res.fields:
            if fld.name == "id":
                streams.add(fld.value)

    return list(streams)


# returns list of stream IDs of matching strings - with a limit and sort alpha
def search_stream_index_alpha_return_names(search_string, limit):
    index = get_stream_index()
    search_results = index.search(
                        query=search.Query(
                            "string: {}".format(search_string),
                            options=search.QueryOptions(
                                limit=limit,
                                sort_options=search.SortOptions(
                                    expressions=[
                                        search.SortExpression(expression='name', default_value='')],
                                    limit=1000),
                                returned_fields=['name']
                                )
                        )
    )
    streams = set()
    for res in search_results:
        streams.add(res.fields[0].value)

    return list(streams)


# meant to be called for a tag or stream object
# must provide the index name
# hack to get partial string searching
def searchablize_tag_or_stream(item, index_name, response):
    index = search.Index(name=index_name, namespace=search_index_namespace)
    if item is None:
        return
    toks = item.name.split()

    try:
        full_str = ""
        for tok in toks:
            for i in range(len(tok)+1):
                for j in range(i):
                    substr = tok[j:i]
                    add_strs = [substr]

                    for s in add_strs:
                        doc = search.Document(fields=[search.AtomField(name='id', value=str(item.key.id())),
                                                      search.TextField(name='name', value=item.name),
                                                      search.TextField(name='string', value=s),
                                                      search.DateField(name='date_added', value=datetime.datetime.now().date())])
                        # Index the document.
                        index.put(doc)
            full_str += " " + tok
    except search.PutError, e:
        result = e.results[0]
        response['errResult'] = str(result)


def remove_stream_from_search_index(stream, response):
    index = get_stream_index()
    if stream is None:
        return

    search_result = index.search("id: {}".format(str(stream.key.id())))
    for doc in search_result.results:
        index.delete(doc.doc_id)
    return


def remove_tag_from_search_index(tag_name, response):
    index = get_tag_index()
    if tag_name in ['', None]:
        return

    search_result = index.search("id: {}".format(str(tag_name)))
    for doc in search_result.results:
        index.delete(doc.doc_id)
    return


def get_tag_index():
    return search.Index(name=get_tag_index_name(), namespace=search_index_namespace)


def get_stream_index():
    return search.Index(name=get_stream_index_name(), namespace=search_index_namespace)


def set_stream_index_name(new_name):
    search_info = SearchInfo.get_by_id(search_index_namespace)
    if search_info is None:
        search_info = SearchInfo(id=search_index_namespace, tag_index_name='tag_index', stream_index_name='stream_index')
    search_info.stream_index_name = new_name
    search_info.put()


def set_tag_index_name(new_name):
    search_info = SearchInfo.get_by_id(search_index_namespace)
    if search_info is None:
        search_info = SearchInfo(id = search_index_namespace, tag_index_name='tag_index', stream_index_name='stream_index')
    search_info.tag_index_name = new_name
    search_info.put()


def get_stream_index_name():
    search_info = SearchInfo.get_by_id(search_index_namespace)
    if search_info is None:
        search_info = SearchInfo(id=search_index_namespace, tag_index_name='tag_index', stream_index_name='stream_index')
        search_info.put()
    return search_info.stream_index_name


def get_tag_index_name():
    search_info = SearchInfo.get_by_id(search_index_namespace)
    if search_info is None:
        search_info = SearchInfo(id=search_index_namespace, tag_index_name='tag_index', stream_index_name='stream_index')
        search_info.put()
    return search_info.tag_index_name


def get_image_range_param(handler):
    image_range = handler.get_request_param(image_range_parm)
    if image_range is None:
        return None, None, "No image range found"

    # verify image range format
    m = re.match("^([\d]+)-([\d]+)$", image_range)
    if m is None:
        return None, None, "Incorrect image range format. Expected <number>-<number>"

    # get the indices
    inds = sorted([int(ind) for ind in m.groups()])
    return inds[0], inds[1], "good range"


def render_html_template(path, template_values_dict):
    return template.render(path, template_values_dict)



# [START link-helpers}
import os
base_url = 'http://{0}'.format(os.environ['HTTP_HOST'])


def get_viewstream_url(streamid, i1, i2, active=-1):
    if active < 0:
        return '{0}/viewstream?{1}={2};{3}={4}-{5};'.format(base_url, stream_id_parm, streamid, image_range_parm, i1, i2)
    else:
        return '{0}/viewstream?{1}={2};{3}={4}-{5};{6}={7};'.format(base_url, stream_id_parm, streamid, image_range_parm, i1, i2, active_image_parm, active)


def get_viewstream_default_url(streamid):
    return get_viewstream_url(streamid, 1, 10)


def get_tagmod_url_noparm():
    return '{0}/tagmod'.format(base_url)


def get_tagged_streams_url(tagname):
    tagname = urllib2.quote(tagname.strip())
    return '{0}/services/taggedstreams?{1}={2}'.format(base_url, tag_name_parm, tagname)


def get_viewtag_url(tagname):
    tagname = urllib2.quote(tagname.strip())
    return '{0}/viewtag?{1}={2};'.format(base_url, tag_name_parm, tagname)

# [END link-helpers}


# [START service-link-helpers]
def get_addtag_service_url(stream_id, tagname):
    tagname = urllib2.quote(tagname.strip())
    return '{0}/services/addstreamtag?{1}={2};{3}={4}'.format(base_url, stream_id_parm, stream_id, tag_name_parm, tagname)


def get_removetag_service_url(stream_id, tagname):
    tagname = urllib2.quote(tagname.strip())
    return '{0}/services/removestreamtag?{1}={2};{3}={4}'.format(base_url, stream_id_parm, stream_id, tag_name_parm, tagname)


def get_viewstream_service_url(streamid, i1, i2):
    return '{0}/services/viewstream?{1}={2};{3}={4}-{5};'.format(base_url, stream_id_parm, streamid, image_range_parm, i1, i2)


def get_subscribed_service_url(userid, streamid):
    return '{0}/services/subscribed?{1}={2};{3}={4};'.format(base_url, user_id_parm, userid, stream_id_parm, streamid)


def get_subscribe_service_url(userid, streamid, redirect):
    return '{0}/services/subscribe?{1}={2};{3}={4};{5}={6};'.format(base_url, user_id_parm, userid, stream_id_parm,
                                                             streamid, redirect_parm, redirect)


def get_unsubscribe_service_url(userid, streamid, redirect):
    return '{0}/services/unsubscribe?{1}={2};{3}={4};{5}={6};'.format(base_url, user_id_parm, userid, stream_id_parm,
                                                             streamid, redirect_parm, redirect)

# [END service-link-helpers]
