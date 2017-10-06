import json
import re
import datetime

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
message_parm = 'code'
# [END HTTP request parameter names]

# [START ERROR CODES]
error_codes = {
    111: 'Stream view already exists! Please choose another name!'
}
# [END ERROR CODES]


search_index_namespace = 'connexion'
tag_index_name = 'tag_index'
stream_index_name = 'stream_index'


# [START HTTP request methods]
# currently using webapp2 request handlers

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
    searchablize_tag_or_stream(tag, tag_index_name, response)


def searchablize_stream(stream, response={}):
    searchablize_tag_or_stream(stream, stream_index_name, response)


def search_tag_index(search_string):
    index = search.Index(name=tag_index_name, namespace=search_index_namespace)
    search_results = index.search("string: {}".format(search_string))
    tags = set()
    for res in search_results:
        for fld in res.fields:
            if fld.name == "id":
                tags.add(fld.value)
    return list(tags)


# returns list of stream IDs of matching strings
def search_stream_index(search_string):
    index = search.Index(name=stream_index_name, namespace=search_index_namespace)
    search_results = index.search("string: {}".format(search_string))
    streams = set()
    for res in search_results:
        for fld in res.fields:
            if fld.name == "id":
                streams.add(fld.value)

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
        for tok in toks:
            for i in range(len(tok)):
                substr = tok[0:i+1]
                doc = search.Document(fields=[search.TextField(name='id', value=str(item.key.id())),
                                              search.TextField(name='name', value=item.name),
                                              search.TextField(name='string', value=substr),
                                              search.DateField(name='date_added', value=datetime.datetime.now().date())])
                # Index the document.
                index.put(doc)
    except search.PutError, e:
        result = e.results[0]
        response['errResult'] = str(result)


def remove_stream_from_search_index(stream, response):
    index = search.Index(name=stream_index_name, namespace=search_index_namespace)
    if stream is None:
        return

    search_result = index.search("id: {}".format(str(stream.key.id())))
    print("\n{}\n".format(search_result))
    for doc in search_result.results:
        index.delete(doc.doc_id)
    return


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
