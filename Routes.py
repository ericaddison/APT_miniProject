import webapp2
from source.services.Service_CreateTag import CreateTagService

config = {'webapp2_extras.sessions': {'secret_key': 'my-super-secret-key'}}

app = webapp2.WSGIApplication([

# [START views]
# [END views]

# [START services]
    ('/services/createtag', CreateTagService)
# [END services]

], config=config, debug=True)