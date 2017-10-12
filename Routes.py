import webapp2

from source.services.Service_CreateStream import CreateStreamService
from source.services.Service_CreateTag import CreateTagService
from source.services.Service_DeleteStream import DeleteStreamService
from source.services.Service_Subscribe import SubscribeToStreamService, UnsubscribeFromStreamService, CheckSubscribedService
from source.services.Service_UploadFile import UploadFileHandler
from source.services.Service_ViewStream import ViewStreamService
from source.services.Service_TextSearch import TagTextSearchService, StreamTextSearchService
from source.services.Service_Management import ManagementService
from source.services.Service_StreamsForTag import StreamsForTagService
from source.services.Service_Tag import AddTagToStreamService, RemoveTagFromStreamService
from source.services.Service_Autcomplete import AutocompleteService
from source.services.Service_CronRebuildSearchIndex import CronRebuildSearchIndexService
from source.services.Service_StreamInfo import BatchStreamInfoService
from source.views.Create import CreatePage
from source.views.Delete import DeletePage, DeleteExe
from source.views.Unsubscribe import UnsubscribePage, UnsubscribeExe
from source.views.ViewStream import ViewStream, TagMod
from source.views.ViewTag import ViewTag
from source.views.TextSearch import TextSearch, TextSearchForm
from source.views.ErrorView import ErrorView
from source.views.ViewAllStreams import ViewAllStreams
from source.views.Social import SocialPage
from source.Main import ManagePage

config = {'webapp2_extras.sessions': {'secret_key': 'my-super-secret-key'}}

app = webapp2.WSGIApplication([

    # [START views]
    ('/create', CreatePage),
    ('/viewall', ViewAllStreams),
    ('/delete', DeletePage),
    ('/deleteexe', DeleteExe),
    ('/unsubscribe', UnsubscribePage),
    ('/unsubscribeexe', UnsubscribeExe),
    ('/viewstream', ViewStream),
    ('/viewtag', ViewTag),
    ('/search', TextSearchForm),
    ('/searchexe', TextSearch),
    ('/error', ErrorView),
    ('/manage', ManagePage),
    ('/tagmod', TagMod),
    ('/social', SocialPage),
    # [END views]

    # [START services]
    ('/services/createtag', CreateTagService),
    ('/services/createstream', CreateStreamService),
    ('/services/subscribe', SubscribeToStreamService),
    ('/services/unsubscribe', UnsubscribeFromStreamService),
    ('/services/upload', UploadFileHandler),
    ('/services/viewstream', ViewStreamService),
    ('/services/deletestream', DeleteStreamService),
    ('/services/searchtags', TagTextSearchService),
    ('/services/searchstreams', StreamTextSearchService),
    ('/services/management', ManagementService),
    ('/services/subscribed', CheckSubscribedService),
    ('/services/addstreamtag', AddTagToStreamService),
    ('/services/removestreamtag', RemoveTagFromStreamService),
    ('/services/taggedstreams', StreamsForTagService),
    ('/services/autocomplete', AutocompleteService),
    ('/services/rebuildindices', CronRebuildSearchIndexService)
    ('/services/streaminfo', BatchStreamInfoService)
    # [END services]

], config=config, debug=True)
