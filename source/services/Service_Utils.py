import json
import re
from google.appengine.ext import ndb
from google.appengine.api import search
import datetime

stream_id_parm = 'streamID'
user_id_parm = 'userID'
image_range_parm = 'imageRange'
tag_name_parm = 'tagName'
search_parm = 'searchString'
search_results_parm = 'searchResults'

search_index_namespace = 'connexion'
tag_index_name = 'tag_index'
stream_index_name = 'stream_index'


def bad_request_error(handler, response_dict, error_msg):
    response_dict['error'] = error_msg
    handler.response.set_status(400)
    handler.response.write(json.dumps(response_dict))
    return


def write_response(handler, response_text):
    handler.response.write(response_text)


def get_tag_param(handler):
    return handler.request.get(tag_name_parm)


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
    search_string = handler.request.get(search_parm)
    if search_string is None:
        response['error'] = "No searchString found"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    response[search_parm] = search_string
    return search_string


def get_search_results_param(handler, response):
    # request parameter error checking
    search_results = handler.request.get(search_results_parm)
    response['search_results'] = search_results
    return search_results


def get_tags_param(handler, response):
    # request parameter error checking
    tags = handler.request.get('tags')
    response['tags'] = tags
    return tags


def get_stream_param(handler, response):
    # request parameter error checking
    stream_id = handler.request.get(stream_id_parm)
    if stream_id is None:
        response['error'] = "No streamID found"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    response[stream_id_parm] = stream_id

    # retrieve the stream from the ID
    stream = (ndb.Key('Stream', int(stream_id))).get()

    if stream is None:
        response['error'] = "Invalid stream ID"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    return stream


def get_user_param(handler, response):
    user_id = handler.request.get(user_id_parm)
    if user_id is None:
        response['error'] = "No userID found"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    # retrieve request parameters
    response[user_id_parm] = user_id

    # retrieve the user from the ID
    user = (ndb.Key('StreamUser', user_id)).get()

    if user is None:
        response['error'] = "Invalid user ID"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    return user


def get_image_range_param(handler, response):
    image_range = handler.request.get(image_range_parm)
    if image_range is None:
        response['error'] = "No image range found"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    # verify image range format
    m = re.match("^([\d]+)-([\d]+)$", image_range)
    if m is None:
        response['error'] = "Incorrect image range format. Expected <number>-<number>"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    # get the indices
    return sorted([int(ind) for ind in m.groups()])
