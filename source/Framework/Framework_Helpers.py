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
    return filehandler.get_uploads()[index]


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


def searchablize_tag(tag, response):
    searchablize_tag_or_stream(tag, tag_index_name, response)


def searchablize_stream(stream, response):
    searchablize_tag_or_stream(stream, stream_index_name, response)


# meant to be called for a tag or stream object
# must provide the index name
# hack to get partial string searching
def searchablize_tag_or_stream(item, index_name, response):
    index = search.Index(name=index_name, namespace=search_index_namespace)
    toks = item.name.split()

    try:
        for tok in toks:
            for i in range(len(tok)):
                substr = tok[0:i+1]
                doc = search.Document(fields=[search.TextField(name='name', value=item.name),
                                              search.TextField(name='string', value=substr),
                                              search.DateField(name='date_added', value=datetime.datetime.now().date())])
                # Index the document.
                index.put(doc)
    except search.PutError, e:
        result = e.results[0]
        response['errResult'] = str(result)


def get_search_string_param(handler, response):
    # request parameter error checking
    search_string = handler.request.get(search_string_parm)
    if search_string is None:
        response['error'] = "No searchString found"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    response[search_string_parm] = search_string
    return search_string


def get_search_results_param(handler, response):
    # request parameter error checking
    search_results = handler.request.get(search_results_parm)
    response['search_results'] = search_results
    return search_results


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