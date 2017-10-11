import os

from google.appengine.api import users

from google.appengine.api import app_identity
from source.models.NdbClasses import *
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler
from google.appengine.ext.webapp import template
import json


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

        # 100x100 image on pin mouseover.
        # Need: StreamID, Lat, Long, ImageURL, DateAdded
        # get all items
        
        all_streamItems = StreamItem.query().fetch()
        item_loc = []
        for item in all_streamItems:
            if item.getLatLng() is not None:
                oneItem = []
                
                oneItem.append(item.stream.id())
                oneItem.append(item.dateAdded.strftime("%Y-%m-%d %H:%M:%S"))
                
                if item.URL is None:
                    imageURL = fh.get_file_url(item.blobKey)
                else:
                    imageURL = item.URL
                
                oneItem.append(imageURL)
                oneItem.append(item.latitude)
                oneItem.append(item.longitude)
                
                item_loc.append(oneItem)

        
        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': user,
            'login_url': login_url,
            'login_text': login_text,
            'app': app_identity.get_application_id(),
            'streamItems': all_streamItems,
            'streamItemsLoc': json.dumps(item_loc)}

        path = os.path.join(os.path.dirname(__file__), '../../templates/GeoMap.html')
        self.set_content_text_html()
        self.write_response(fh.render_html_template(path, template_values))

