import webapp2
from source.services.Service_CreateTag import CreateTagService
from source.services.Service_CreateStream import CreateStreamService
from source.services.Service_Subscribe import SubscribeToStreamService, UnsubscribeFromStreamService

config = {'webapp2_extras.sessions': {'secret_key': 'my-super-secret-key'}}

app = webapp2.WSGIApplication([

    # [START views]
    # [END views]

    # [START services]
    ('/services/createtag', CreateTagService),
    ('/services/createstream', CreateStreamService),
    ('/services/subscribe', SubscribeToStreamService),
    ('/services/unsubscribe', UnsubscribeFromStreamService)
    # [END services]

], config=config, debug=True)
