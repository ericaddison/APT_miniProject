import webapp2
from webapp2_extras import sessions
from google.appengine.ext.webapp import blobstore_handlers

# a base class for all request handlers in our app
# includes session setup
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        sess = self.session_store.get_session()

        #add some default values:
        if not sess.get('test_session_prop'):
            sess['test_session_prop']='howdy!'
        return sess

    def get_request_param(self, param_name):
        return self.request.get(param_name)

    def write_response(self, response_text):
        self.response.write(response_text)

    def get_request_parameter_dictionary(self):
        return self.request.params

    def set_content_text_plain(self):
        self.response.content_type = 'text/plain'

    def set_content_text_html(self):
        self.response.content_type = 'text/html'

    def redirect(self, url):
        super(BaseHandler, self).redirect(url)


# file handler. Currently just extends BaseHandler and google blobstoreUpload handler
class FileUploadHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    @classmethod
    def nothing(cls):
        print("place-holder")
