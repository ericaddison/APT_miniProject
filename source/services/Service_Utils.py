import json
import re
from google.appengine.ext import ndb

stream_id_parm = 'streamID'
user_id_parm = 'userID'
image_range_parm = 'imageRange'


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
