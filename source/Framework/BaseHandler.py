import webapp2
from webapp2_extras import sessions
from source.services import *


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