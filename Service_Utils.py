import json
from google.appengine.ext import ndb

stream_id_parm = 'streamID'
user_id_parm = 'userID'


def get_stream_param(handler, response):
    # request parameter error checking
    if stream_id_parm not in handler.request.GET.keys():
        response['error'] = "No streamID found"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    stream_id = handler.request.GET[stream_id_parm]
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
    if user_id_parm not in handler.request.GET.keys():
        response['error'] = "No userID found"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    # retrieve request parameters
    user_id = handler.request.GET[user_id_parm]
    response[user_id_parm] = user_id

    # retrieve the user from the ID
    user = (ndb.Key('StreamUser', user_id)).get()

    if user is None:
        response['error'] = "Invalid user ID"
        handler.response.set_status(400)
        handler.response.write(json.dumps(response))
        return

    return user