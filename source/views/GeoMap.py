import os

from google.appengine.api import users

from google.appengine.api import app_identity
from source.models.NdbClasses import *
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler
from google.appengine.ext.webapp import template


class GeoMapPage(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        # get all items
        all_streamItems = StreamItem.query().fetch()
        item_loc = []
        for item in all_streamItems:
            if item.getLatLng() is not None:
                item_loc.append(item.getLatLng())
        
        testing2 = all_streamItems[0].getLatLng()

        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user,
            'login_url': login_url,
            'login_text': login_text,
            'app': app_identity.get_application_id(),
            'streamItems': all_streamItems,
            'streamItemsLoc': item_loc,
            'testing': "{lat: 30.2893746, lng: -97.7349663}",
            'testing2': testing2}

        path = os.path.join(os.path.dirname(__file__), '../../templates/GeoMap.html')
        self.set_content_text_html()
        self.write_response(fh.render_html_template(path, template_values))

