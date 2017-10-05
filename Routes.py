import webapp2

from source.services.Service_CreateStream import CreateStreamService
from source.services.Service_CreateTag import CreateTagService
from source.services.Service_DeleteStream import DeleteStreamService
from source.services.Service_Subscribe import SubscribeToStreamService, UnsubscribeFromStreamService
from source.services.Service_UploadFile import UploadFileHandler
from source.services.Service_ViewStream import ViewStreamService
from source.services.Service_Management import ManagementService
from source.views.Create import CreatePage
from source.views.Delete import DeletePage, DeleteExe
from source.views.Unsubscribe import UnsubscribePage, UnsubscribeExe
from source.views.ViewStream import ViewStream
from source.views.TextSearch import TextSearch, TextSearchForm
from source.views.ErrorView import ErrorView
from source.Main import ManagePage

config = {'webapp2_extras.sessions': {'secret_key': 'my-super-secret-key'}}

app = webapp2.WSGIApplication([

    # [START views]
    ('/create', CreatePage),
    ('/delete', DeletePage),
    ('/deleteexe', DeleteExe),
    ('/unsubscribe', UnsubscribePage),
    ('/unsubscribeexe', UnsubscribeExe),
    ('/viewstream', ViewStream),
    ('/search', TextSearchForm),
    ('/searchexe', TextSearch),
    ('/error', ErrorView),
    ('/manage', ManagePage),
    # [END views]

    # [START services]
    ('/services/createtag', CreateTagService),
    ('/services/createstream', CreateStreamService),
    ('/services/subscribe', SubscribeToStreamService),
    ('/services/unsubscribe', UnsubscribeFromStreamService),
    ('/services/upload', UploadFileHandler),
    ('/services/viewstream', ViewStreamService),
    ('/services/deletestream', DeleteStreamService),
    ('/services/management', ManagementService)
    # [END services]

], config=config, debug=True)
